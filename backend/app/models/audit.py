"""
Audit log model for UCC Event Manager.
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class AuditLog(Base):
    """Audit log model for security events."""
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        index=True,
    )
    
    # Event information
    event_type = Column(
        String(50),
        nullable=False,
        index=True,
    )
    event_category = Column(
        String(50),
        nullable=False,
        index=True,
    )
    severity = Column(
        String(20),
        nullable=False,
        default="info",
    )
    
    # User relationship (nullable for anonymous events)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    
    # Event details
    description = Column(
        Text,
        nullable=False,
    )
    details = Column(
        JSON,
        nullable=True,
    )
    
    # Request information
    ip_address = Column(
        String(45),
        nullable=True,
    )
    user_agent = Column(
        Text,
        nullable=True,
    )
    request_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    
    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="audit_logs",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, event_type={self.event_type}, user_id={self.user_id})>"


# Predefined audit event types
class AuditEventType:
    """Predefined audit event types."""
    
    # Authentication events
    AUTH_LOGIN_SUCCESS = "auth.login.success"
    AUTH_LOGIN_FAILURE = "auth.login.failure"
    AUTH_LOGOUT = "auth.logout"
    AUTH_TOKEN_REFRESH = "auth.token.refresh"
    AUTH_TOKEN_REVOKE = "auth.token.revoke"
    AUTH_ACCOUNT_LOCKED = "auth.account.locked"
    
    # Password events
    PASSWORD_RESET_REQUEST = "password.reset.request"
    PASSWORD_RESET_SUCCESS = "password.reset.success"
    PASSWORD_CHANGE = "password.change"
    
    # MFA events
    MFA_ENABLE = "mfa.enable"
    MFA_DISABLE = "mfa.disable"
    MFA_VERIFY_SUCCESS = "mfa.verify.success"
    MFA_VERIFY_FAILURE = "mfa.verify.failure"
    MFA_BACKUP_CODE_USED = "mfa.backup_code.used"
    
    # User events
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    
    # Event management
    EVENT_CREATE = "event.create"
    EVENT_UPDATE = "event.update"
    EVENT_DELETE = "event.delete"
    
    # Security events
    SECURITY_SUSPICIOUS_ACTIVITY = "security.suspicious_activity"
    SECURITY_RATE_LIMIT_EXCEEDED = "security.rate_limit.exceeded"
    SECURITY_INVALID_REQUEST = "security.invalid_request"
    
    # Admin events
    ADMIN_USER_CREATE = "admin.user.create"
    ADMIN_USER_UPDATE = "admin.user.update"
    ADMIN_USER_DELETE = "admin.user.delete"
    ADMIN_SYSTEM_ACCESS = "admin.system.access"


class AuditEventCategory:
    """Audit event categories."""
    
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    USER_MANAGEMENT = "user_management"
    DATA_ACCESS = "data_access"
    SECURITY = "security"
    ADMIN = "admin"
    SYSTEM = "system"


class AuditEventSeverity:
    """Audit event severity levels."""
    
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical" 