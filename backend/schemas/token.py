"""Pydantic schemas for token-related operations."""
from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """OAuth2.0 token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    scope: str = "read write"


class TokenRefreshRequest(BaseModel):
    """Token refresh request schema."""
    grant_type: str = Field(..., pattern="^refresh_token$")
    refresh_token: str = Field(..., min_length=1)


class TokenRevokeRequest(BaseModel):
    """Token revocation request schema."""
    token: str = Field(..., min_length=1)
    token_type_hint: str = Field(default="refresh_token", pattern="^(access_token|refresh_token)$") 