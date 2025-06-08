"""
User repository for database operations.
"""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
from app.models.user import User


class UserRepository:
    """Repository for user-related database operations."""
    logger = structlog.get_logger(__name__)
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            db_session: The SQLAlchemy database session.
        """
        self._db_session = db_session

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Fetch a user from the database by their ID.

        Args:
            user_id: The ID of the user to fetch.

        Returns:
            The user object if found, otherwise None.
        """
        return await self._db_session.get(User, user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieves a user from the database by email."""
        stmt = select(User).where(User.email == email.lower())
        result = await self._db_session.execute(stmt)
        return result.scalar_one_or_none()