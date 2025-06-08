"""
Event management endpoints for UCC Event Manager.
"""
from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from schemas import event as event_schema
from app.services.event_service import EventService
from app.core import get_current_active_user, get_async_session

router = APIRouter()


@router.post(
    "/",
    response_model=event_schema.EventRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Event",
    description="Create a new event for the authenticated user.",
)
async def create_event(
    event_in: event_schema.EventCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Creates a new event in the system.

    This endpoint allows an authenticated user to create a new event associated
    with their account.

    - **`title`**: The title of the event (required).
    - **`occurrence`**: The date and time of the event in ISO 8601 format (required).
    - **`description`**: An optional description for the event.
    """
    service = EventService(db)
    new_event = await service.create_event(
        event_data=event_in, current_user=current_user
    )
    return new_event


@router.get(
    "/",
    response_model=event_schema.PaginatedEventRead,
    summary="List User Events",
    description="Get a paginated list of events for the authenticated user, with options for sorting and filtering.",
)
async def list_events(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
    offset: int = Query(0, ge=0, description="Number of events to skip."),
    limit: int = Query(50, ge=1, le=100, description="Number of events to return."),
    sort: Literal["occurrence", "created_at", "title"] = Query(
        "occurrence", description="Field to sort by."
    ),
    order: Literal["asc", "desc"] = Query("asc", description="Sort order."),
    from_date: datetime | None = Query(
        None, description="Filter events from this date (ISO 8601 format)."
    ),
    to_date: datetime | None = Query(
        None, description="Filter events to this date (ISO 8601 format)."
    ),
):
    """
    Retrieves a list of events for the currently authenticated user.

    Supports pagination, sorting, and date range filtering.
    """
    service = EventService(db)
    events, total = await service.get_user_events(
        current_user=current_user,
        offset=offset,
        limit=limit,
        sort=sort,
        order=order,
        from_date=from_date,
        to_date=to_date,
    )
    return event_schema.PaginatedEventRead(
        total=total, limit=limit, offset=offset, data=events
    )


@router.get(
    "/{event_id}",
    response_model=event_schema.EventRead,
    summary="Get Single Event",
    description="Get details of a specific event by its ID.",
)
async def get_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieves a single event by its unique ID.

    The endpoint ensures that the user requesting the event is the owner.
    """
    service = EventService(db)
    event = await service.get_event_by_id(
        event_id=event_id, current_user=current_user
    )
    return event


@router.patch(
    "/{event_id}",
    response_model=event_schema.EventRead,
    summary="Update Event",
    description="Update an event's description. Only the description field can be changed.",
)
async def update_event(
    event_id: UUID,
    event_in: event_schema.EventUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Updates the description of a specific event.

    The endpoint first verifies that the event exists and belongs to the
    authenticated user before applying the update.
    """
    service = EventService(db)
    updated_event = await service.update_event(
        event_id=event_id, event_data=event_in, current_user=current_user
    )
    return updated_event


# TODO: Implement other event endpoints
# - DELETE /events/{event_id} 