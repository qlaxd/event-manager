"""
Event model for UCC Event Manager.
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Event(Base):
    """Event model for user-created events."""
    
    __tablename__ = "events"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        index=True,
    )
    
    # Event fields
    title = Column(
        String(255),
        nullable=False,
        index=True,
    )
    occurrence = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    description = Column(
        Text,
        nullable=True,
    )
    
    # User relationship
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    
    # Soft delete
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    user: "User" = relationship(
        "User",
        back_populates="events",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<Event(id={self.id}, title={self.title}, user_id={self.user_id})>"
    
    @property
    def is_deleted(self) -> bool:
        """Check if event is soft deleted."""
        return self.deleted_at is not None 