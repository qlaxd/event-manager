"""
Main FastAPI application for UCC Event Manager.
"""
import logging
from contextlib import asynccontextmanager
import sys  # Add at the top if not already imported

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from structlog import get_logger

from app.api.v1 import auth, users, events, helpdesk, health
from app.core.config import settings, validate_settings
from app.core.database import init_db, close_db
from app.utils.logging import setup_logging
from app.utils.exceptions import setup_exception_handlers
import dotenv
dotenv.load_dotenv()

# Setup structured logging
setup_logging()
logger = get_logger()

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    Handles startup and shutdown tasks.
    """
    # Startup
    logger.info("Starting UCC Event Manager API", version=settings.APP_VERSION)
    
    # Validate settings
    try:
        validate_settings()
        logger.info("Settings validated successfully")
    except AssertionError as e:
        logger.error("Settings validation failed", error=str(e))
        raise
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down UCC Event Manager API")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json" if not settings.ENVIRONMENT == "production" else None,
    docs_url=f"{settings.API_V1_PREFIX}/docs" if settings.DEBUG else None,
    redoc_url=f"{settings.API_V1_PREFIX}/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Add state for rate limiter
app.state.limiter = limiter

# Add exception handler for rate limits
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup custom exception handlers
setup_exception_handlers(app)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Add security headers from config
    for header, value in settings.SECURITY_HEADERS.items():
        response.headers[header] = value
    
    # Add additional headers
    response.headers["X-Request-ID"] = request.state.request_id if hasattr(request.state, "request_id") else "unknown"
    
    return response

# Add request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to each request."""
    import uuid
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Log request
    logger.info(
        "Request received",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_host=request.client.host if request.client else "unknown",
    )
    
    response = await call_next(request)
    
    # Log response
    logger.info(
        "Request completed",
        request_id=request_id,
        status_code=response.status_code,
    )
    
    return response

# Print loaded CORS origins for debugging
print("DEBUG: BACKEND_CORS_ORIGINS =", settings.BACKEND_CORS_ORIGINS, file=sys.stderr)



# Configure CORS
if settings.BACKEND_CORS_ORIGINS:
    print("DEBUG: Adding CORS middleware with origins:", [str(origin) for origin in settings.BACKEND_CORS_ORIGINS], file=sys.stderr)
    app.add_middleware(
        CORSMiddleware,
        #allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_origins=["http://localhost:5173"], # TODO: Remove this, this is for development only
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
        max_age=3600,
    )

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["api.ucc-event-manager.com", "localhost"],
)

# Include API routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"],
)

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_PREFIX}/users",
    tags=["Users"],
)

app.include_router(
    events.router,
    prefix=f"{settings.API_V1_PREFIX}/events",
    tags=["Events"],
)

app.include_router(
    helpdesk.router,
    prefix=f"{settings.API_V1_PREFIX}/helpdesk",
    tags=["Helpdesk"],
)

# Health check router (no prefix for easy monitoring)
app.include_router(
    health.router,
    tags=["Health"],
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": f"{settings.API_V1_PREFIX}/docs" if settings.DEBUG else None,
        "health": "/health",
    }

# Global 404 handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors with consistent format."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "not_found",
            "error_description": f"The requested resource '{request.url.path}' was not found",
            "request_id": getattr(request.state, "request_id", "unknown"),
        }
    )

# Global 500 handler
@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors with consistent format."""
    logger.error(
        "Internal server error",
        request_id=getattr(request.state, "request_id", "unknown"),
        error=str(exc),
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "error_description": "An internal server error occurred. Please try again later.",
            "request_id": getattr(request.state, "request_id", "unknown"),
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_config=None,  # Use structlog instead
    ) 