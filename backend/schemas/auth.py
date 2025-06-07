"""Pydantic schemas for authentication."""
from typing import Optional

from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel


class AuthResponse(BaseModel):
    """Generic authentication response."""
    message: str


class OAuth2PasswordRequestFormWithMFA(OAuth2PasswordRequestForm):
    """Extended OAuth2 form with MFA support."""
    
    def __init__(
        self,
        *,
        grant_type: str = Form(default=None, pattern="password"),
        username: str = Form(),
        password: str = Form(),
        scope: str = Form(default=""),
        client_id: Optional[str] = Form(default=None),
        client_secret: Optional[str] = Form(default=None),
        mfa_code: Optional[str] = Form(default=None, pattern="^[0-9]{6}$")
    ):
        super().__init__(
            grant_type=grant_type,
            username=username,
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret
        )
        self.mfa_code = mfa_code 