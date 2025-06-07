"""
Health check endpoints for UCC Event Manager.
"""
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_async_session, check_database_health

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Basic health check endpoint.
    Returns the current status of the API.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/health/detailed", response_model=Dict[str, Any])
async def detailed_health_check(db: AsyncSession = Depends(get_async_session)):
    """
    Detailed health check endpoint.
    Checks database connectivity and other services.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {}
    }
    
    # Check database
    try:
        db_healthy = await check_database_health()
        health_status["checks"]["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "message": "Database is accessible" if db_healthy else "Database connection failed"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database check failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Check Rasa chatbot (if configured)
    if settings.RASA_URL:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{settings.RASA_URL}/status", timeout=5.0)
                rasa_healthy = response.status_code == 200
                health_status["checks"]["chatbot"] = {
                    "status": "healthy" if rasa_healthy else "unhealthy",
                    "message": "Rasa chatbot is accessible" if rasa_healthy else "Rasa chatbot is not responding"
                }
        except Exception as e:
            health_status["checks"]["chatbot"] = {
                "status": "unhealthy",
                "message": f"Rasa check failed: {str(e)}"
            }
    
    return health_status


@router.get("/ready", response_model=Dict[str, str])
async def readiness_check():
    """
    Readiness check endpoint for kubernetes.
    """
    # Check if all required services are ready
    db_healthy = await check_database_health()
    
    if not db_healthy:
        raise HTTPException(
            status_code=503,
            detail="Service is not ready"
        )
    
    return {"status": "ready"}


@router.get("/live", response_model=Dict[str, str])
async def liveness_check():
    """
    Liveness check endpoint for kubernetes.
    """
    return {"status": "alive"} 