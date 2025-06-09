from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.models.auth import RefreshToken
from typing import Optional, Tuple, List
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

    async def get_by_id(self, token_id: uuid.UUID) -> Optional[RefreshToken]:
        """Get a refresh token by its ID."""
        return await self.db.get(RefreshToken, token_id)

    async def get_all_by_user_id(
        self, user_id: uuid.UUID, offset: int, limit: int
    ) -> Tuple[List[RefreshToken], int]:
        """
        Get all active refresh tokens for a user with pagination.
        Returns a tuple of (tokens, total_count).
        """
        stmt = (
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .order_by(RefreshToken.issued_at.desc())
            .offset(offset)
            .limit(limit)
        )
        count_stmt = (
            select(func.count())
            .select_from(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        )
        
        result = await self.db.execute(stmt)
        tokens = result.scalars().all()
        
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()
        
        return tokens, total

    async def revoke_by_id(self, token_id: uuid.UUID) -> Optional[RefreshToken]:
        """Revokes a specific refresh token by its ID."""
        token = await self.get_by_id(token_id)
        if token and not token.revoked_at:
            token.revoked_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(token)
            return token
        return None

    async def revoke_all_for_user(self, user_id: uuid.UUID):
        """Revokes all active refresh tokens for a given user."""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await self.db.execute(stmt)
        await self.db.commit() 