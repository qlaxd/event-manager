"""
Event management endpoints for UCC Event Manager.
"""
from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Request, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from schemas import event as event_schema
from app.services.event_service import EventService
from app.core import get_current_active_user, get_async_session
from app.core.security import get_current_active_user_optional
from app.utils.api_keys import get_service_api_key
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/",
    response_model=event_schema.EventRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Event",
    description="Create a new event for the authenticated user or via service API.",
)
@limiter.limit("10/minute")
async def create_event(
    request: Request,
    event_in: event_schema.EventCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User | None = Depends(get_current_active_user_optional),
    is_service: bool | None = Depends(get_service_api_key),
    user_id: UUID | None = Query(None, description="User ID for service API calls"),
):
    """
    Creates a new event in the system.

    This endpoint allows:
    1. An authenticated user to create a new event associated with their account
    2. A service (like Rasa) to create an event on behalf of a user using an API key

    For user authentication:
    - The user must be authenticated with a valid JWT token
    - The event will be associated with the authenticated user

    For service authentication:
    - The service must provide a valid API key in the X-Service-API-Key header
    - The service must specify the user_id in the request body or as a query parameter

    Request body:
    - **`title`**: The title of the event (required).
    - **`occurrence`**: The date and time of the event in ISO 8601 format (required).
    - **`description`**: An optional description for the event.
    - **`user_id`**: The ID of the user to create the event for (can be in body or query param).
    """
    service = EventService(db)
    
    # Determine the authentication method
    if current_user:
        # User is authenticated via JWT
        new_event = await service.create_event(event_data=event_in, current_user=current_user)
    elif is_service:
        # Service is authenticated via API key
        # Check for user_id in query parameter first, then in request body
        service_user_id = user_id or event_in.user_id
        if not service_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id is required for service API calls (either in request body or as a query parameter)"
            )
        new_event = await service.create_event(event_data=event_in, user_id=service_user_id)
    else:
        # No valid authentication
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return new_event


@router.get(
    "/",
    response_model=event_schema.PaginatedEventRead,
    summary="List User Events",
    description="Get a paginated list of events for the authenticated user, with options for sorting and filtering.",
)
@limiter.limit("10/minute")
async def list_events(
    request: Request,
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
@limiter.limit("10/minute")
async def get_event(
    request: Request,
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


# PATCH /events/{event_id}
# - Update Event
# - Only the description field can be changed.
# - The endpoint first verifies that the event exists and belongs to the
# - authenticated user before applying the update.

@router.patch(
    "/{event_id}",
    response_model=event_schema.EventRead,
    summary="Update Event",
    description="Update an event's description. Only the description field can be changed.",
)
@limiter.limit("10/minute")
async def update_event(
    request: Request,
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


# DELETE /events/{event_id}
# - Delete Event
# - The endpoint first verifies that the event exists and belongs to the
# - authenticated user before deleting it.

@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Event",
    description="Delete an event by its ID.",
)
@limiter.limit("10/minute")
async def delete_event(
    request: Request,
    event_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Deletes a specific event.

    The endpoint ensures the user owns the event before deletion.
    Returns 204 No Content on successful deletion.
    """
    service = EventService(db)
    await service.delete_event(event_id=event_id, current_user=current_user)
    return None


