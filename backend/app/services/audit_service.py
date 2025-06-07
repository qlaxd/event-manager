"""
Audit service for UCC Event Manager.
Handles security event logging and audit trails.
"""
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.audit import AuditLog

logger = structlog.get_logger(__name__)

def _map_event_to_category_and_severity(event_type: str) -> Tuple[str, str]:
    """Maps event type to a category and severity level."""
    if "FAILURE" in event_type or "ERROR" in event_type:
        severity = "high"
    elif "SUCCESS" in event_type:
        severity = "info"
    else:
        severity = "medium"

    if "AUTH" in event_type:
        category = "Authentication"
    elif "USER" in event_type:
        category = "UserManagement"
    elif "ADMIN" in event_type:
        category = "AdminAction"
    else:
        category = "General"
    
    return category, severity


async def log_security_event(
    db: AsyncSession,
    event_type: str,
    user_id: Optional[UUID] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[UUID] = None,
    error_message: Optional[str] = None,
):
    """Logs a security-related event."""
    try:
        event_category, severity = _map_event_to_category_and_severity(event_type)
        
        description = f"Security event: {event_type}"
        if error_message:
            description += f" - Error: {error_message}"
        
        audit_log = AuditLog(
            user_id=user_id,
            event_type=event_type,
            event_category=event_category,
            severity=severity,
            description=description,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
        )
        
        db.add(audit_log)
        await db.commit()
        
        logger.info(
            "Security event logged",
            event_type=event_type,
            user_id=str(user_id) if user_id else None,
            ip_address=ip_address
        )
        
    except Exception as e:
        logger.error(
            "Failed to log security event",
            event_type=event_type,
            user_id=str(user_id) if user_id else None,
            error=str(e)
        )


async def log_user_action(
    db: AsyncSession,
    user_id: UUID,
    action: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[UUID] = None,
    error_message: Optional[str] = None,
):
    """Logs a user action."""
    try:
        event_category, severity = "UserAction", "info"
        
        description = f"User action: {action}"
        if error_message:
            description += f" - Error: {error_message}"
            severity = "warning"

        audit_log = AuditLog(
            user_id=user_id,
            event_type=action,
            event_category=event_category,
            severity=severity,
            description=description,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
        )

        db.add(audit_log)
        await db.commit()

    except Exception as e:
        logger.error(
            "Failed to log user action",
            user_id=str(user_id),
            action=action,
            error=str(e),
        )

async def log_admin_action(
    db: AsyncSession,
    admin_user_id: UUID,
    action: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[UUID] = None,
    error_message: Optional[str] = None,
):
    """Logs an admin action."""
    try:
        event_category, severity = "AdminAction", "warning"

        description = f"Admin action: {action}"
        if error_message:
            description += f" - Error: {error_message}"
            severity = "high"

        audit_log = AuditLog(
            user_id=admin_user_id,
            event_type=action,
            event_category=event_category,
            severity=severity,
            description=description,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
        )

        db.add(audit_log)
        await db.commit()

    except Exception as e:
        logger.error(
            "Failed to log admin action",
            admin_user_id=str(admin_user_id),
            action=action,
            error=str(e),
        ) 