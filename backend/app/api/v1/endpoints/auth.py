"""
Authentication endpoints for UCC Event Manager.

Implements OAuth2.0 password flow with JWT tokens, MFA support, 
password reset functionality, and comprehensive security measures.
"""

import structlog
from fastapi import APIRouter, Depends, Request, status, HTTPException
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


@router.post("/revoke", status_code=status.HTTP_200_OK)
@limiter.limit("20/minute")
async def revoke_refresh_token(
    request: Request,
    token_data: TokenRevokeRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Revoke a refresh token (logout).

    This endpoint invalidates a specified refresh token, effectively logging out
    the session associated with it. This action requires the user to be authenticated
    with a valid access token. The token to be revoked must be a refresh token.
    """
    if token_data.token_type_hint and token_data.token_type_hint != "refresh_token":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported token type. Only 'refresh_token' can be revoked.",
        )

    await AuthService.revoke_refresh_token(
        db=db,
        request=request,
        ip_address=get_remote_address(request),
        token_to_revoke=token_data.token,
        current_user=current_user,
    )
    return JSONResponse(content={"message": "Token revoked successfully"})


# Password Management Endpoints

@router.post("/password-reset/request", status_code=status.HTTP_200_OK)
@limiter.limit("3/hour")
async def request_password_reset(
    request: Request,
    reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Request a password reset token.
    
    This endpoint initiates the password reset process. It accepts an email address
    and, if a corresponding active user account exists, sends an email with a
    password reset link. To prevent user enumeration attacks, this endpoint
    will always return a successful response, regardless of whether the email
    address is in the system or not.
    """
    response = await AuthService.request_password_reset(
        db=db,
        request=request,
        ip_address=get_remote_address(request),
        email=reset_request.email.lower().strip(),
    )
    return JSONResponse(content=response)


@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
@limiter.limit("25/15minutes")
async def confirm_password_reset(
    request: Request,
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Confirm a password reset using a token.
    
    This endpoint allows a user to set a new password using the token sent
    to their email. The token is single-use and expires after a configured
    duration. On success, the user's password is updated. On failure, a generic
    error is returned to prevent security risks.
    """
    response = await AuthService.confirm_password_reset(
        db=db,
        request=request,
        ip_address=get_remote_address(request),
        token=reset_data.token,
        new_password=reset_data.new_password,
    )
    return JSONResponse(content=response)


# MFA Management Endpoints

@router.post(
    "/mfa/enable",
    response_model=MFAEnableResponse,
    status_code=status.HTTP_200_OK,
    summary="Initiate MFA enablement",
    description="Initiates the MFA enablement process for the authenticated user. "
                "Verifies the user's password and returns an MFA secret, QR code, "
                "and backup codes. The user must then verify with a TOTP code to finalize.",
    dependencies=[Depends(get_current_user)]
)
async def enable_mfa(
    request: Request,
    payload: MFAEnableRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint to initiate the process of enabling Multi-Factor Authentication (MFA).

    Requires the user's current password for verification.
    """
    client_ip = get_remote_address(request)
    try:
        result = await MFAService.enable_mfa(
            db=db, user=current_user, password=payload.password, ip_address=client_ip
        )
        return result
    except HTTPException as e:
        # Re-raise HTTPExceptions from the service layer to return proper error responses
        raise e
    except Exception as e:
        # Log unexpected errors for debugging
        logger.error("MFA enablement failed with an unexpected error", error=e, user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during MFA setup.",
        )
