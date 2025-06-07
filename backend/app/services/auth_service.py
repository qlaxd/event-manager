from fastapi import HTTPException, Request
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

class AuthService:
    """
    Encapsulates all business logic for authentication, authorization,
    and user session management.
    """
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
        user = await UserRepository.get_by_email(db, email)

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