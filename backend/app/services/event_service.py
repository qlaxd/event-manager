"""
Service layer for event-related business logic.
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.event import Event
from app.models.user import User
from app.repositories.event_repository import EventRepository
from schemas.event import EventCreate, EventUpdate


class EventService:
    """Orchestrates business logic for events."""

    def __init__(self, db_session: AsyncSession):
        """
        Initializes the service with a database session.

        :param db_session: The asynchronous database session.
        """
        self.repository = EventRepository(db_session)

    async def create_event(
        self, *, event_data: EventCreate, current_user: User
    ) -> Event:
        """
        Creates a new event for the current user.

        :param event_data: Data for the new event.
        :param current_user: The user creating the event.
        :return: The newly created event.
        """
        # Business logic can be added here in the future, e.g., checking
        # for overlapping events or enforcing limits.
        
        new_event = await self.repository.create(
            event_data=event_data, user_id=current_user.id
        )

        # Other services (e.g., notifications) could be called here.

        return new_event

    async def get_user_events(
        self,
        *,
        current_user: User,
        offset: int,
        limit: int,
        sort: str,
        order: str,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> tuple[list[Event], int]:
        """
        Retrieves a paginated list of events for the current user.

        :param current_user: The user requesting the events.
        :param offset: The number of events to skip.
        :param limit: The maximum number of events to return.
        :param sort: The field to sort by.
        :param order: The sort order.
        :param from_date: The start date to filter events.
        :param to_date: The end date to filter events.
        :return: A tuple containing the list of events and the total count.
        """
        return await self.repository.get_all_by_user_id(
            user_id=current_user.id,
            offset=offset,
            limit=limit,
            sort=sort,
            order=order,
            from_date=from_date,
            to_date=to_date,
        )

    async def get_event_by_id(self, *, event_id: UUID, current_user: User) -> Event:
        """
        Retrieves a single event by its ID, ensuring it belongs to the current user.

        :param event_id: The ID of the event to retrieve.
        :param current_user: The user requesting the event.
        :raises HTTPException: If the event is not found or does not belong to the user.
        :return: The requested event.
        """
        db_event = await self.repository.get_by_id(event_id=event_id)

        if not db_event or db_event.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )
        
        return db_event

    async def update_event(
        self, *, event_id: UUID, event_data: EventUpdate, current_user: User
    ) -> Event:
        """
        Updates an event's description after verifying ownership.

        :param event_id: The ID of the event to update.
        :param event_data: The data for the event update (description only).
        :param current_user: The user performing the update.
        :return: The updated event.
        """
        # First, get the event and verify ownership
        db_event = await self.get_event_by_id(
            event_id=event_id, current_user=current_user
        )

        # Get the update data, excluding unset fields to avoid overwriting with None
        update_data = event_data.model_dump(exclude_unset=True)

        # Call the repository to perform the update
        updated_event = await self.repository.update(
            db_event=db_event, event_data=update_data
        )
        
        return updated_event

    async def delete_event(self, *, event_id: UUID, current_user: User) -> None:
        """
        Deletes an event after verifying ownership.

        :param event_id: The ID of the event to delete.
        :param current_user: The user performing the deletion.
        """
        # First, get the event and verify ownership
        db_event = await self.get_event_by_id(
            event_id=event_id, current_user=current_user
        )

        # Call the repository to perform the soft delete
        await self.repository.delete(db_event=db_event)
