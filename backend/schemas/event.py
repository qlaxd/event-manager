"""Pydantic schemas for Event model."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Base schema for event attributes
class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, example="Team Meeting")
    description: Optional[str] = Field(None, max_length=500, example="Discuss project status.")
    occurrence: datetime = Field(..., example="2024-12-31T23:59:59Z")


# Schema for creating an event
class EventCreate(EventBase):
    pass


# Schema for updating an event
class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100, example="Updated Team Meeting")
    description: Optional[str] = Field(None, max_length=500, example="Updated project status discussion.")
    occurrence: Optional[datetime] = Field(None, example="2025-01-01T10:00:00Z")


# Schema for event data returned by the API
class Event(EventBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Schema for event data as stored in the database
class EventInDB(Event):
    pass 