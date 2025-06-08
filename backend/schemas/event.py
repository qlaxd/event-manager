"""Pydantic schemas for Event model."""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class EventBase(BaseModel):
    """Base schema with common event fields."""
    title: str = Field(..., min_length=1, max_length=255)
    occurrence: datetime
    description: str | None = Field(default=None, max_length=10000)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Team Meeting",
                "occurrence": "2024-10-20T10:00:00Z",
                "description": "Weekly sync-up meeting.",
            }
        }


class EventCreate(EventBase):
    """Schema for creating an event."""
    pass


class EventUpdate(BaseModel):
    """
    Schema for updating an event. Only the description is updatable as per requirements.
    """
    description: str | None = Field(default=None, max_length=10000)

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Updated: Weekly sync-up meeting and project planning.",
            }
        }


class EventRead(EventBase):
    """Response model for reading an event."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedEventRead(BaseModel):
    """Response model for paginated event lists."""
    total: int
    limit: int
    offset: int
    data: list[EventRead] 