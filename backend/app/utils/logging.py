"""
Logging configuration for UCC Event Manager.
Uses structlog for structured logging.
"""
import logging
import sys
from typing import Any, Dict

import structlog
from structlog.stdlib import LoggerFactory

from app.core.config import settings


def setup_logging():
    """Configure structured logging for the application."""
    
    # Set up standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # Structlog processors
    timestamper = structlog.processors.TimeStamper(fmt="iso")
    
    # Development processors (pretty printing)
    dev_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer()
    ]
    
    # Production processors (JSON output)
    prod_processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer()
    ]
    
    # Choose processors based on environment
    processors = dev_processors if settings.DEBUG else prod_processors
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a configured logger instance."""
    return structlog.get_logger(name)


class LoggingMiddleware:
    """Middleware to add logging context to requests."""
    
    def __init__(self, logger: structlog.BoundLogger = None):
        self.logger = logger or get_logger(__name__)
    
    async def __call__(self, request, call_next):
        """Add request context to logs."""
        # Bind request information to logger
        logger = self.logger.bind(
            request_id=getattr(request.state, "request_id", "unknown"),
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
        )
        
        # Store logger in request state for use in endpoints
        request.state.logger = logger
        
        response = await call_next(request)
        return response


def log_audit_event(
    event_type: str,
    event_category: str,
    description: str,
    user_id: str = None,
    severity: str = "info",
    details: Dict[str, Any] = None,
    request_id: str = None,
    ip_address: str = None,
    user_agent: str = None,
):
    """
    Log an audit event.
    This is a placeholder that should integrate with the AuditLog model.
    """
    logger = get_logger("audit")
    
    logger.log(
        severity,
        description,
        event_type=event_type,
        event_category=event_category,
        user_id=user_id,
        details=details,
        request_id=request_id,
        ip_address=ip_address,
        user_agent=user_agent,
    ) 