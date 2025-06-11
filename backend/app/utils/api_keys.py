"""
API key authentication for service-to-service communication.
"""
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import secrets
from typing import Optional

from app.core.config import settings

API_KEY_HEADER = APIKeyHeader(name="X-Service-API-Key", auto_error=False)

async def get_service_api_key(api_key_header: str = Security(API_KEY_HEADER)) -> Optional[bool]:
    """
    Validate the service API key provided in the request header.
    
    Args:
        api_key_header: The API key from the X-Service-API-Key header
        
    Returns:
        True if the API key is valid, None otherwise
    """
    if api_key_header and secrets.compare_digest(api_key_header, settings.RASA_SERVICE_API_KEY):
        return True
    return None 