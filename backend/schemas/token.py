"""
Pydantic schemas for token-related data for the UCC Event Manager.
"""
from pydantic import BaseModel, Field


class Token(BaseModel):
    """
    Response model for the login endpoint.
    Provides the tokens needed for an authenticated session.
    """
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    """
    Represents the data encoded within a JWT access token.
    """
    sub: str | None = None  # 'sub' (subject) claim, e.g., user ID
    exp: int | None = None  # 'exp' (expiration time) claim 


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