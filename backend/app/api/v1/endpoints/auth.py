"""
Authentication endpoints for UCC Event Manager.

Implements OAuth2.0 password flow with JWT tokens, MFA support, 
password reset functionality, and comprehensive security measures.
"""

import structlog
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import get_current_user
from app.models.user import User
from schemas.auth import AuthResponse, OAuth2PasswordRequestFormWithMFA
from schemas.mfa import (
    MFAEnableRequest,
    MFAEnableResponse,
    MFADisableRequest,
    MFAVerifyRequest,
)
from schemas.password import PasswordResetRequest, PasswordResetConfirm
from schemas.token import TokenRefreshRequest, TokenResponse, TokenRevokeRequest
from app.services.audit_service import log_security_event
from app.services.auth_service import AuthService
from app.services.mfa_service import MFAService

# Initialize router and limiter
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = structlog.get_logger(__name__)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# Authentication Endpoints

@router.post("/token", response_model=TokenResponse)
@limiter.limit("5/15minutes")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestFormWithMFA = Depends(),
    db: AsyncSession = Depends(get_async_session)
):
    """
    OAuth2.0 password flow authentication endpoint.
    
    Authenticates user with email/password and optional MFA code.
    Returns JWT access and refresh tokens on successful authentication.
    """
    token_data = await AuthService.login(
        db=db,
        request=request,
        ip_address=get_remote_address(request),
        email=form_data.username.lower().strip(),
        password=form_data.password,
        mfa_code=form_data.mfa_code,
    )
    return TokenResponse(**token_data)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")
async def refresh_access_token(
    request: Request,
    token_data: TokenRefreshRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Refresh expired access token using refresh token.
    
    Validates refresh token and issues new access/refresh token pair.
    """
    refreshed_token_data = await AuthService.refresh_token(
        db=db,
        request=request,
        ip_address=get_remote_address(request),
        refresh_token=token_data.refresh_token,
    )
    return TokenResponse(**refreshed_token_data)


# @router.post("/revoke")
# @limiter.limit("10/minute")
# async def revoke_refresh_token(token_data: TokenRevokeRequest):
#     return TokenResponse()


