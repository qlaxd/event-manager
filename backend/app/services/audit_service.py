"""
Audit service for UCC Event Manager.
Handles security event logging and audit trails.
"""
from datetime import datetime
from typing import Optional, Dict, Any
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog

logger = structlog.get_logger(__name__)


async def log_security_event(
    db: AsyncSession,
    event_type: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log a security event to the audit trail.
    
    Args:
        db: Database session
        event_type: Type of security event
        user_id: ID of the user involved (if applicable)
        ip_address: IP address of the request
        user_agent: User agent string
        details: Additional event details
    """
    try:
        audit_log = AuditLog(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
            timestamp=datetime.utcnow()
        )
        
        db.add(audit_log)
        await db.commit()
        
        # Also log to structured logger
        logger.info(
            "Security event logged",
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            details=details
        )
        
    except Exception as e:
        logger.error(
            "Failed to log security event",
            event_type=event_type,
            user_id=user_id,
            error=str(e)
        )
        # Don't raise exception to avoid breaking the main flow


async def log_user_action(
    db: AsyncSession,
    user_id: str,
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log a user action to the audit trail.
    
    Args:
        db: Database session
        user_id: ID of the user performing the action
        action: Action performed
        resource_type: Type of resource affected
        resource_id: ID of the resource affected
        ip_address: IP address of the request
        details: Additional action details
    """
    try:
        audit_log = AuditLog(
            event_type="USER_ACTION",
            user_id=user_id,
            ip_address=ip_address,
            details={
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                **(details or {})
            },
            timestamp=datetime.utcnow()
        )
        
        db.add(audit_log)
        await db.commit()
        
        logger.info(
            "User action logged",
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id
        )
        
    except Exception as e:
        logger.error(
            "Failed to log user action",
            user_id=user_id,
            action=action,
            error=str(e)
        )


async def log_admin_action(
    db: AsyncSession,
    admin_user_id: str,
    action: str,
    target_user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an admin action to the audit trail.
    
    Args:
        db: Database session
        admin_user_id: ID of the admin performing the action
        action: Action performed
        target_user_id: ID of the user being affected (if applicable)
        resource_type: Type of resource affected
        resource_id: ID of the resource affected
        ip_address: IP address of the request
        details: Additional action details
    """
    try:
        audit_log = AuditLog(
            event_type="ADMIN_ACTION",
            user_id=admin_user_id,
            ip_address=ip_address,
            details={
                "action": action,
                "target_user_id": target_user_id,
                "resource_type": resource_type,
                "resource_id": resource_id,
                **(details or {})
            },
            timestamp=datetime.utcnow()
        )
        
        db.add(audit_log)
        await db.commit()
        
        logger.warning(
            "Admin action logged",
            admin_user_id=admin_user_id,
            action=action,
            target_user_id=target_user_id,
            resource_type=resource_type,
            resource_id=resource_id
        )
        
    except Exception as e:
        logger.error(
            "Failed to log admin action",
            admin_user_id=admin_user_id,
            action=action,
            error=str(e)
        ) 