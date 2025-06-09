"""
Pydantic schemas for token-related data for the UCC Event Manager.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import uuid


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


class SessionRead(BaseModel):
    """Schema for a single user session (active refresh token)."""
    id: uuid.UUID
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    issued_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class PaginatedSessionRead(BaseModel):
    """Schema for paginated session responses."""
    total: int
    limit: int
    offset: int
    data: List[SessionRead] 