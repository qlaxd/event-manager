"""
User repository for database operations.
"""
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Repository for user-related database operations."""

    def __init__(self, db_session: Session):
        """
        Initialize the repository with a database session.

        Args:
            db_session: The SQLAlchemy database session.
        """
        self._db_session = db_session

    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Fetch a user from the database by their ID.

        Args:
            user_id: The ID of the user to fetch.

        Returns:
            The user object if found, otherwise None.
        """
        return self._db_session.get(User, user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Fetch a user from the database by their email.

        Args:
            email: The email of the user to fetch.

        Returns:
            The user object if found, otherwise None.
        """
        statement = select(User).where(User.email == email)
        return self._db_session.execute(statement).scalar_one_or_none()
