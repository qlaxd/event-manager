"""Service layer for user management operations."""
import uuid
from typing import Tuple, List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.user import User
from app.models.auth import RefreshToken
from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from schemas.user import UserUpdate
from schemas.password import PasswordChange
from app.core.security import SecurityUtils
from app.services.audit_service import log_security_event


class UserService:
    """Encapsulates business logic for user profile and session management."""
    logger = structlog.get_logger(__name__)

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)

    async def update_profile(self, current_user: User, update_data: UserUpdate) -> User:
        """Updates a user's profile."""
        updated_user = await self.user_repo.update(current_user, update_data)
        await log_security_event(
            db=self.db,
            event_type="PROFILE_UPDATED",
            user_id=current_user.id,
            details={"updated_fields": list(update_data.model_dump(exclude_unset=True).keys())}
        )
        return updated_user

    async def change_password(self, current_user: User, password_data: PasswordChange):
        """Changes a user's password and revokes all active sessions."""
        if not SecurityUtils.verify_password(password_data.current_password, current_user.hashed_password):
            await log_security_event(
                db=self.db,
                event_type="PASSWORD_CHANGE_FAILURE",
                user_id=current_user.id,
                details={"reason": "incorrect_current_password"}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password."
            )

        current_user.hashed_password = SecurityUtils.get_password_hash(password_data.new_password)
        self.db.add(current_user)
        
        await self.token_repo.revoke_all_for_user(current_user.id)
        
        await self.db.commit()
        
        await log_security_event(
            db=self.db,
            event_type="PASSWORD_CHANGED",
            user_id=current_user.id
        )
        self.logger.info("User password changed successfully", user_id=current_user.id)

    async def get_sessions(self, current_user: User, offset: int, limit: int) -> Tuple[List[RefreshToken], int]:
        """Gets all active sessions for a user."""
        return await self.token_repo.get_all_by_user_id(current_user.id, offset, limit)

    async def revoke_session(self, current_user: User, session_id: uuid.UUID):
        """Revokes a specific user session."""
        session = await self.token_repo.get_by_id(session_id)

        if not session or session.user_id != current_user.id or session.revoked_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        revoked_token = await self.token_repo.revoke_by_id(session.id)
        if not revoked_token:
            # This case might happen in a race condition, but it's good to handle.
            # The token was found but couldn't be revoked (e.g., already revoked).
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        
        await log_security_event(
            db=self.db,
            event_type="SESSION_REVOKED",
            user_id=current_user.id,
            details={"revoked_session_id": str(session_id)}
        )
        self.logger.info("User session revoked", user_id=current_user.id, session_id=session_id) 