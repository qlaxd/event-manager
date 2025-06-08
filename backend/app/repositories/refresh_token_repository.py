from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.auth import RefreshToken
from typing import Optional
from datetime import datetime, timezone
import uuid


class RefreshTokenRepository:
    """Repository for refresh token database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_jti(self, jti: str) -> Optional[RefreshToken]:
        """Get a refresh token by its JTI."""
        query = select(RefreshToken).where(RefreshToken.jti == jti)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def revoke_all_for_user(self, user_id: uuid.UUID):
        """Revokes all active refresh tokens for a given user."""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await self.db.execute(stmt)
        await self.db.commit() 