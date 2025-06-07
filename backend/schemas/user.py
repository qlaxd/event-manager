"""Pydantic schemas for User model."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# Base schema for user attributes
class UserBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    full_name: str = Field(..., min_length=1, max_length=100, example="John Doe")


# Schema for creating a user
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="strongpassword123")


# Schema for updating a user
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, example="John Doe")
    email: Optional[EmailStr] = Field(None, example="user@example.com")


# Schema for user data returned by the API
class User(UserBase):
    id: UUID
    is_active: bool
    mfa_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Schema for user data as stored in the database
class UserInDB(User):
    password_hash: str
    mfa_secret: Optional[str] = None 