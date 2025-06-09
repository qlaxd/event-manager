"""Pydantic schemas for password-related operations."""
from pydantic import BaseModel, EmailStr, Field, validator
from app.core.security import SecurityUtils


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""
    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""
    token: str = Field(..., min_length=32, max_length=64)
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validate password meets security requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        # Check against common passwords (simplified)
        # TODO: Add a list of common passwords, i guess i can use some library for this
        common_passwords = {'password', '12345678', 'qwerty', 'password123'}
        if v.lower() in common_passwords:
            raise ValueError('Password is too common')
        return v 


class PasswordChange(BaseModel):
    """Schema for changing a user's password."""
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)

    @validator("new_password")
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        is_valid, message = SecurityUtils.validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v 