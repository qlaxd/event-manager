"""
Repository for database operations on the Event model.
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from schemas.event import EventCreate


class EventRepository:
    """Manages database interactions for events."""

    def __init__(self, db_session: AsyncSession):
        """
        Initializes the repository with a database session.
        
        :param db_session: The asynchronous database session.
        """
        self.db = db_session

    async def create(self, *, event_data: EventCreate, user_id: UUID) -> Event:
        """
        Creates a new event in the database.

        :param event_data: The data for the new event.
        :param user_id: The ID of the user creating the event.
        :return: The newly created Event object.
        """
        new_event = Event(
            **event_data.model_dump(),
            user_id=user_id,
        )
        self.db.add(new_event)
        await self.db.commit()
        await self.db.refresh(new_event)
        return new_event

    async def get_all_by_user_id(
        self,
        *,
        user_id: UUID,
        offset: int,
        limit: int,
        sort: str,
        order: str,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> tuple[list[Event], int]:
        """
        Fetches a paginated list of events for a specific user.

        :param user_id: The ID of the user whose events to fetch.
        :param offset: The number of events to skip.
        :param limit: The maximum number of events to return.
        :param sort: The field to sort by.
        :param order: The sort order ('asc' or 'desc').
        :param from_date: The start date to filter events.
        :param to_date: The end date to filter events.
        :return: A tuple containing the list of events and the total count.
        """
        # Base query for fetching events
        query = select(Event).where(Event.user_id == user_id, Event.deleted_at.is_(None))

        # Date range filtering
        if from_date:
            query = query.where(Event.occurrence >= from_date)
        if to_date:
            query = query.where(Event.occurrence <= to_date)
        
        # Count total matching events before pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_count_result = await self.db.execute(count_query)
        total = total_count_result.scalar_one()

        # Sorting
        sortable_fields = {
            "occurrence": Event.occurrence,
            "created_at": Event.created_at,
            "title": Event.title,
        }
        sort_column = sortable_fields.get(sort, Event.occurrence)

        if order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Pagination
        paginated_query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await self.db.execute(paginated_query)
        events = result.scalars().all()
        
        return events, total

    async def get_by_id(self, *, event_id: UUID) -> Event | None:
        """
        Fetches a single event by its ID.

        :param event_id: The ID of the event to fetch.
        :return: The Event object if found, otherwise None.
        """
        query = select(Event).where(
            Event.id == event_id, Event.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
