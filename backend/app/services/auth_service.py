"""
Service layer for authentication operations.
"""
from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.security import SecurityUtils
from schemas.token import TokenResponse
from schemas.mfa import MFAEnableRequest, MFAEnableResponse, MFADisableRequest, MFAVerifyRequest
from schemas.password import PasswordResetRequest, PasswordResetConfirm
from schemas.token import TokenRefreshRequest, TokenRevokeRequest
from app.services.audit_service import log_security_event
from app.services.mfa_service import MFAService
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from app.core.config import settings
import structlog
from app.models.auth import RefreshToken
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.password_reset_token_repository import PasswordResetTokenRepository
from app.services.email_service import send_password_reset_email


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
        user_repo = UserRepository(db)
        user = await user_repo.get_by_email(email)

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
        expires_at = datetime.now(timezone.utc) + timedelta(
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

        user.last_login_at = datetime.now(timezone.utc)
        user.last_login_ip = ip_address
        await db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    @staticmethod
    async def request_password_reset(
        db: AsyncSession, request: Request, ip_address: str, email: str
    ):
        """
        Handles a password reset request.
        Generates a token, saves it, and sends a reset email.
        """
        user_repo = UserRepository(db)
        user = await user_repo.get_by_email(email)

        # To prevent user enumeration attacks, we don't reveal if the user was found.
        # We will proceed as if we are sending an email, but only do so if the user exists.
        if user and user.is_active:
            try:
                # Generate a secure token
                reset_token = secrets.token_urlsafe(32)
                token_hash = AuthService._hash_token(reset_token)

                # Store the token hash in the database
                token_repo = PasswordResetTokenRepository(db)
                await token_repo.create_token(
                    user_id=user.id,
                    token_hash=token_hash,
                    expires_in_minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES,
                )

                # Send the password reset email
                email_sent = await send_password_reset_email(
                    email=user.email, name=user.full_name, token=reset_token
                )

                await log_security_event(
                    db=db,
                    event_type="PASSWORD_RESET_REQUEST",
                    user_id=user.id,
                    ip_address=ip_address,
                    details={"email": email, "email_sent": email_sent},
                )

                if email_sent:
                    AuthService.logger.info("Password reset email sent", email=email)
                else:
                    AuthService.logger.error("Password reset request failed, email could not be sent", email=email)
            except Exception as e:
                AuthService.logger.error(
                    "Error during password reset process",
                    email=email,
                    error=str(e),
                )
        else:
            AuthService.logger.info(
                "Password reset requested for non-existent or inactive user",
                email=email,
            )
        
        # Always return a generic success message
        return {"message": "If an account with that email exists, a password reset link has been sent."}

    @staticmethod
    async def refresh_token(
        db: AsyncSession,
        request: Request,
        ip_address: str,
        refresh_token: str,
    ):
        """
        Handles refresh token validation and issues a new token pair.
        Implements refresh token rotation for enhanced security.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = SecurityUtils.decode_token(refresh_token)
            if payload.get("type") != "refresh":
                AuthService.logger.warning(
                    "Invalid token type for refresh", token_payload=payload
                )
                raise credentials_exception

            user_id = payload.get("sub")
            jti = payload.get("jti")
            if not user_id or not jti:
                AuthService.logger.warning(
                    "Missing user_id or jti in refresh token", token_payload=payload
                )
                raise credentials_exception
        except Exception as e:
            AuthService.logger.warning("Refresh token decoding failed", error=str(e))
            raise credentials_exception

        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            AuthService.logger.warning(
                "Refresh token failure: user not found or inactive.",
                user_id=user_id,
                is_active=getattr(user, "is_active", None),
            )
            await log_security_event(
                db=db,
                event_type="AUTH_REFRESH_FAILURE",
                user_id=user.id if user else None,
                ip_address=ip_address,
                details={"reason": "user_not_found_or_inactive", "user_id": user_id},
            )
            raise credentials_exception

        token_repo = RefreshTokenRepository(db)
        db_refresh_token = await token_repo.get_by_jti(jti)

        if not db_refresh_token:
            AuthService.logger.warning(
                "Refresh token failure: JTI not found in DB.", jti=jti
            )
            await log_security_event(
                db=db,
                event_type="AUTH_REFRESH_FAILURE",
                user_id=user.id,
                ip_address=ip_address,
                details={"reason": "refresh_token_not_found", "jti": jti},
            )
            raise credentials_exception

        if db_refresh_token.revoked_at is not None:
            await log_security_event(
                db=db,
                event_type="AUTH_REFRESH_FAILURE_REUSE",
                user_id=user.id,
                ip_address=ip_address,
                details={
                    "reason": "attempted_reuse_of_revoked_refresh_token",
                    "jti": jti,
                },
            )
            raise credentials_exception

        token_hash = AuthService._hash_token(refresh_token)
        if not secrets.compare_digest(db_refresh_token.token_hash, token_hash):
            AuthService.logger.warning(
                "Refresh token failure: token hash mismatch.", jti=jti
            )
            await log_security_event(
                db=db,
                event_type="AUTH_REFRESH_FAILURE",
                user_id=user.id,
                ip_address=ip_address,
                details={"reason": "token_hash_mismatch", "jti": jti},
            )
            raise credentials_exception

        if db_refresh_token.expires_at < datetime.now(timezone.utc):
            AuthService.logger.warning(
                "Refresh token failure: expired refresh token.", jti=jti
            )
            await log_security_event(
                db=db,
                event_type="AUTH_REFRESH_FAILURE",
                user_id=user.id,
                ip_address=ip_address,
                details={"reason": "expired_refresh_token", "jti": jti},
            )
            raise credentials_exception

        db_refresh_token.revoked_at = datetime.now(timezone.utc)
        await db.commit()

        new_jti = secrets.token_urlsafe(32)
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        new_access_token = SecurityUtils.create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires,
        )
        new_refresh_token = SecurityUtils.create_refresh_token(
            data={"sub": str(user.id), "jti": new_jti}
        )

        new_token_hash = AuthService._hash_token(new_refresh_token)
        new_expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        await AuthService._create_refresh_token_record(
            db, user, new_jti, new_token_hash, new_expires_at, request, ip_address
        )

        await log_security_event(
            db=db,
            event_type="AUTH_REFRESH_SUCCESS",
            user_id=user.id,
            ip_address=ip_address,
            details={"new_jti": new_jti, "revoked_jti": jti},
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "expires_in": int(access_token_expires.total_seconds()),
        }

    @staticmethod
    async def revoke_refresh_token(
        db: AsyncSession,
        request: Request,
        ip_address: str,
        token_to_revoke: str,
        current_user: User,
    ):
        """
        Revokes a specific refresh token, making it invalid for future use.
        Ensures that the user revoking the token is its legitimate owner.
        """
        try:
            payload = SecurityUtils.decode_token(token_to_revoke)
            token_type = payload.get("type")
            token_owner_id = payload.get("sub")
            jti = payload.get("jti")

            if token_type != "refresh" or not token_owner_id or not jti:
                AuthService.logger.warning("Invalid refresh token payload for revocation", payload=payload)
                # Don't raise error, to prevent leaking token validity info.
                return
        except Exception as e:
            AuthService.logger.warning("Refresh token decoding failed during revocation", error=str(e))
            # As the token is unusable, we can consider the goal achieved.
            return

        # Critical Security Check: The user authenticated via Bearer token must be the owner of the refresh token.
        if str(current_user.id) != token_owner_id:
            await log_security_event(
                db=db,
                event_type="AUTH_REVOKE_FAILURE",
                user_id=current_user.id,
                ip_address=ip_address,
                details={
                    "reason": "permission_denied",
                    "attempted_revocation_of_jti": jti,
                    "token_owner": token_owner_id,
                },
            )
            # This is a security violation attempt. We must stop here.
            # We don't want to tell the user that the token is valid but belongs to someone else.
            # A generic "Forbidden" is appropriate.
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )

        token_repo = RefreshTokenRepository(db)
        db_token = await token_repo.get_by_jti(jti)

        if not db_token or db_token.is_revoked:
            # If token is not in DB or already revoked, the goal is already met.
            # This can happen if a user tries to revoke the same token twice.
            return
        
        # Additional check to ensure DB record owner matches
        if db_token.user_id != current_user.id:
             await log_security_event(
                db=db,
                event_type="AUTH_REVOKE_FAILURE",
                user_id=current_user.id,
                ip_address=ip_address,
                details={
                    "reason": "db_owner_mismatch",
                    "jti": jti,
                },
            )
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )

        db_token.revoked_at = datetime.now(timezone.utc)
        await db.commit()

        await log_security_event(
            db=db,
            event_type="AUTH_REVOKE_SUCCESS",
            user_id=current_user.id,
            ip_address=ip_address,
            details={"revoked_jti": jti},
        )
        