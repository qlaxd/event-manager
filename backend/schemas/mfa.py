"""Pydantic schemas for MFA-related operations."""
from pydantic import BaseModel, Field


class MFAEnableRequest(BaseModel):
    """MFA enable request schema."""
    password: str = Field(..., min_length=1)


class MFAEnableResponse(BaseModel):
    """MFA enable response schema."""
    secret: str
    qr_code: str
    backup_codes: list[str]


class MFAVerifyRequest(BaseModel):
    """MFA verification request schema."""
    mfa_code: str = Field(..., pattern="^[0-9]{6}$")


class MFADisableRequest(BaseModel):
    """MFA disable request schema."""
    password: str = Field(..., min_length=1)
    mfa_code: str = Field(..., pattern="^[0-9]{6}$") 