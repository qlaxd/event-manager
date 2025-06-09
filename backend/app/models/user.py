"""
User model for UCC Event Manager.
"""
import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, String, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.auth import RefreshToken, PasswordResetToken, MFABackupCode
    from app.models.audit import AuditLog


class User(Base):
    """User model with authentication and MFA support."""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        index=True,
    )
    
    # User information
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    full_name = Column(
        String(255),
        nullable=False,
    )
    hashed_password = Column(
        Text,
        nullable=False,
    )
    
    # Account status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_admin = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    
    # MFA fields
    mfa_enabled = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    mfa_secret = Column(
        String(32),
        nullable=True,
    )
    
    # Password security
    password_changed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    failed_login_attempts = Column(
        Integer,
        default=0,
        nullable=False,
    )
    locked_until = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Login tracking
    last_login_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_login_ip = Column(
        String(45), # Supports IPv6
        nullable=True,
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
    events: Mapped[List["Event"]] = relationship(
        "Event",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    password_reset_tokens: Mapped[List["PasswordResetToken"]] = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    mfa_backup_codes: Mapped[List["MFABackupCode"]] = relationship(
        "MFABackupCode",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
    
    @property
    def is_locked(self) -> bool:
        """Check if user account is locked."""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False 