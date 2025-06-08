"""
Repository for PasswordResetToken model.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.auth import PasswordResetToken
from datetime import datetime, timedelta, timezone
import uuid
from sqlalchemy import select
from typing import Optional

class PasswordResetTokenRepository:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_token(
        self,
        user_id: uuid.UUID,
        token_hash: str,
        expires_in_minutes: int = 60
    ) -> PasswordResetToken:
        """
        Creates and stores a new password reset token.
        """
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        
        new_token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        
        self.db.add(new_token)
        await self.db.commit()
        await self.db.refresh(new_token)
        return new_token 

    async def get_by_token_hash(self, token_hash: str) -> Optional[PasswordResetToken]:
        """Get a password reset token by its hash."""
        result = await self.db.execute(
            select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def delete(self, token: PasswordResetToken):
        """Delete a password reset token."""
        await self.db.delete(token)
        await self.db.commit() 