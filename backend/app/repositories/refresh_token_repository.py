from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.auth import RefreshToken
from typing import Optional


class RefreshTokenRepository:
    """Repository for refresh token database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_jti(self, jti: str) -> Optional[RefreshToken]:
        """Get a refresh token by its JTI."""
        query = select(RefreshToken).where(RefreshToken.jti == jti)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() 