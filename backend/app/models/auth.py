"""
Authentication-related models for UCC Event Manager.
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class RefreshToken(Base):
    """Refresh token model for token revocation support."""
    
    __tablename__ = "refresh_tokens"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        index=True,
    )
    
    # Token fields (JWT ID)
    jti = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    # Token hash (JWT token)
    token_hash = Column(
        Text,
        nullable=False,
    )
    
    # User relationship
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Token metadata
    issued_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    # Token expiration
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # Token revocation
    revoked_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Device information
    user_agent = Column(
        Text,
        nullable=True,
    )
    ip_address = Column(
        String(45),  # Supports IPv6
        nullable=True,
    )
    
    # Relationships
    user: "User" = relationship(
        "User",
        back_populates="refresh_tokens",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, jti={self.jti})>"
    
    @property
    def is_revoked(self) -> bool:
        """Check if token is revoked."""
        return self.revoked_at is not None
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at


class PasswordResetToken(Base):
    """Password reset token model."""
    
    __tablename__ = "password_reset_tokens"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        index=True,
    )
    
    # Token fields
    token_hash = Column(
        Text,
        unique=True,
        nullable=False,
        index=True,
    )
    
    # User relationship
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Token metadata
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    used_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Request information
    ip_address = Column(
        String(45),
        nullable=True,
    )
    
    # Relationships
    user: "User" = relationship(
        "User",
        back_populates="password_reset_tokens",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id})>"
    
    @property
    def is_used(self) -> bool:
        """Check if token has been used."""
        return self.used_at is not None
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if token is valid (not used and not expired)."""
        return not self.is_used and not self.is_expired


class MFABackupCode(Base):
    """MFA backup code model."""
    
    __tablename__ = "mfa_backup_codes"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        index=True,
    )
    
    # Code fields
    code_hash = Column(
        Text,
        nullable=False,
        index=True,
    )
    
    # User relationship
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Usage tracking
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    used_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    user: "User" = relationship(
        "User",
        back_populates="mfa_backup_codes",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<MFABackupCode(id={self.id}, user_id={self.user_id})>"
    
    @property
    def is_used(self) -> bool:
        """Check if backup code has been used."""
        return self.used_at is not None 