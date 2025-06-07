"""
Service layer for authentication operations.
"""
from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.models.user import User
from repositories.user_repository import UserRepository
from app.core.security import SecurityUtils
from schemas.token import TokenResponse
from schemas.mfa import MFAEnableRequest, MFAEnableResponse, MFADisableRequest, MFAVerifyRequest
from schemas.password import PasswordResetRequest, PasswordResetConfirm
from schemas.token import TokenRefreshRequest, TokenRevokeRequest
from app.services.audit_service import log_security_event
from app.services.mfa_service import MFAService
import secrets
import hashlib
from datetime import datetime, timedelta
from app.core.config import settings
import structlog
from app.models.auth import RefreshToken


class AuthService:
    """
    Encapsulates all business logic for authentication, authorization,
    and user session management.
    """
    logger = structlog.get_logger(__name__)
    
    @staticmethod
    async def _create_refresh_token_record(
        db: AsyncSession,
        user: User,
        jti: str,
        token_hash: str,
        expires_at: datetime,
        request: Request,
        ip_address: str,
    ):
        """Creates a new refresh token record in the database."""
        refresh_token = RefreshToken(
            jti=jti,
            token_hash=token_hash,
            user_id=user.id,
            expires_at=expires_at,
            user_agent=request.headers.get("User-Agent"),
            ip_address=ip_address,
        )
        db.add(refresh_token)
        await db.commit()

    @staticmethod
    def _hash_token(token: str) -> str:
        """Hashes a token for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    async def login(
        db: AsyncSession,
        request: Request,
        ip_address: str,
        email: str,
        password: str,
        mfa_code: Optional[str],
    ):
        """
        Handles the user login process, including password and MFA verification.
        Returns a new set of tokens upon success.
        """
        user = await UserRepository._get_user_by_email(db, email)

        # Log the authentication attempt
        await log_security_event(
            db=db,
            event_type="AUTH_ATTEMPT",
            user_id=user.id if user else None,
            ip_address=ip_address,
            user_agent=request.headers.get("User-Agent"),
            details={"email": email, "mfa_provided": bool(mfa_code)},
        )

        if not user or not SecurityUtils.verify_password(password, user.hashed_password):
            await log_security_event(
                db=db,
                event_type="AUTH_FAILURE",
                user_id=user.id if user else None,
                ip_address=ip_address,
                details={"reason": "invalid_credentials", "email": email},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            await log_security_event(
                db=db,
                event_type="AUTH_FAILURE",
                user_id=user.id,
                ip_address=ip_address,
                details={"reason": "account_inactive"},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive"
            )

        if user.mfa_enabled:
            if not mfa_code:
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="Multi-factor authentication code required",
                )
            if not await MFAService.verify_login_code(db, user, mfa_code, ip_address):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid multi-factor authentication code",
                )
            
        jti = secrets.token_urlsafe(32)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = SecurityUtils.create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires,
        )
        refresh_token = SecurityUtils.create_refresh_token(
            data={"sub": str(user.id), "jti": jti}
        )

        token_hash = AuthService._hash_token(refresh_token)
        expires_at = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        await AuthService._create_refresh_token_record(
            db, user, jti, token_hash, expires_at, request, ip_address
        )

        await log_security_event(
            db=db,
            event_type="AUTH_SUCCESS",
            user_id=user.id,
            ip_address=ip_address,
            details={"mfa_used": user.mfa_enabled},
        )

        user.last_login_at = datetime.utcnow()
        user.last_login_ip = ip_address
        await db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
        