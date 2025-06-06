"""
Exception handling utilities for UCC Event Manager.
"""
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from structlog import get_logger

logger = get_logger(__name__)


class AppException(Exception):
    """Base application exception."""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Dict[str, Any] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(AppException):
    """Authentication failed exception."""
    
    def __init__(self, message: str = "Authentication failed", details: Dict = None):
        super().__init__(
            error_code="authentication_failed",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class AuthorizationError(AppException):
    """Authorization failed exception."""
    
    def __init__(self, message: str = "Insufficient permissions", details: Dict = None):
        super().__init__(
            error_code="authorization_failed",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class NotFoundError(AppException):
    """Resource not found exception."""
    
    def __init__(self, resource: str, resource_id: str = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with id {resource_id} not found"
        
        super().__init__(
            error_code="not_found",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ConflictError(AppException):
    """Resource conflict exception."""
    
    def __init__(self, message: str = "Resource conflict", details: Dict = None):
        super().__init__(
            error_code="conflict",
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class ValidationError(AppException):
    """Validation error exception."""
    
    def __init__(self, message: str = "Validation error", details: Dict = None):
        super().__init__(
            error_code="validation_error",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class RateLimitError(AppException):
    """Rate limit exceeded exception."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
            
        super().__init__(
            error_code="rate_limit_exceeded",
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details,
        )


def setup_exception_handlers(app: FastAPI):
    """Set up global exception handlers for the application."""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """Handle application exceptions."""
        logger.warning(
            exc.message,
            error_code=exc.error_code,
            status_code=exc.status_code,
            details=exc.details,
            request_id=getattr(request.state, "request_id", "unknown"),
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "error_description": exc.message,
                "details": exc.details,
                "request_id": getattr(request.state, "request_id", "unknown"),
            },
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        errors = {}
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            if field not in errors:
                errors[field] = []
            errors[field].append(error["msg"])
        
        logger.warning(
            "Request validation failed",
            errors=errors,
            request_id=getattr(request.state, "request_id", "unknown"),
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "validation_error",
                "error_description": "Request validation failed",
                "details": errors,
                "request_id": getattr(request.state, "request_id", "unknown"),
            },
        )
    
    @app.exception_handler(IntegrityError)
    async def database_integrity_error_handler(request: Request, exc: IntegrityError):
        """Handle database integrity errors."""
        logger.error(
            "Database integrity error",
            error=str(exc),
            request_id=getattr(request.state, "request_id", "unknown"),
        )
        
        # Don't expose database details in production
        if app.debug:
            message = str(exc)
        else:
            message = "A database constraint was violated"
        
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "database_error",
                "error_description": message,
                "request_id": getattr(request.state, "request_id", "unknown"),
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(
            "Unexpected error occurred",
            error=str(exc),
            exc_info=True,
            request_id=getattr(request.state, "request_id", "unknown"),
        )
        
        # Don't expose internal errors in production
        if app.debug:
            message = str(exc)
        else:
            message = "An unexpected error occurred"
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_server_error",
                "error_description": message,
                "request_id": getattr(request.state, "request_id", "unknown"),
            },
        ) 