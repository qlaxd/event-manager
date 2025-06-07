# Professional Endpoint Development Guide: UCC Event Manager

## 1. Introduction
This guide provides a comprehensive, step-by-step process for professionally developing a new backend endpoint for the UCC Event Manager. Adhering to this process ensures that all endpoints are secure, scalable, maintainable, and consistent with the project's architecture.

The process is divided into four main phases:
1.  **Planning & Design**: Understanding the requirements and defining the contracts.
2.  **Implementation**: Writing the code across the different layers of the application.
3.  **Testing**: Ensuring the endpoint is robust and bug-free.
4.  **Finalization**: Integrating security, documentation, and logging.

We will use the **"Create a New Event"** feature (`POST /api/v1/events`) as a running example to illustrate each step.

---

## 2. Phase 1: Planning & Design

Before writing a single line of code, it's crucial to have a clear plan.

### 2.1 Understand the Requirements
-   **Source of Truth**: Review the project's core documents:
    -   **Product Requirements (`prd.md`)**: What is the business goal? Who is the user? (e.g., US-004: "As a user, I want to create a new event...")
    -   **API Specifications (`api-specs.md`)**: What is the exact request/response contract? (e.g., `POST /events` with title, occurrence, and optional description).
    -   **Security Document (`security.md`)**: What are the security constraints? (e.g., All API endpoints require valid authentication).

### 2.2 Define the API Contract
-   **Endpoint**: `POST /api/v1/events`
-   **Request Body**:
    -   `title`: string, required
    -   `occurrence`: datetime, required
    -   `description`: string, optional
-   **Success Response (201 Created)**:
    -   The full event object, including `id`, `created_at`, etc.
-   **Error Responses**:
    -   `401 Unauthorized`: If the user is not authenticated.
    -   `422 Unprocessable Entity`: If validation fails (e.g., missing title).

---

## 3. Phase 2: Implementation (The Code)

Follow the existing project structure (`docs/backend/file-structure.md`) to keep the codebase organized. The process flows from the outside in: defining data structures, then implementing logic from the database up to the API layer.

### Step 1: Define Schemas (`app/schemas/`)
Pydantic schemas define the data structures for your API. They are used for request validation and response serialization.

-   **Why?**: This enforces a strict data contract, prevents invalid data from entering your system, and automatically generates documentation.

**Example (`app/schemas/event.py`):**
```python
from pydantic import BaseModel
from datetime import datetime
import uuid

# Schema for the request body when creating an event
class EventCreate(BaseModel):
    title: str
    occurrence: datetime
    description: str | None = None

# Schema for the response body when reading an event
class EventRead(BaseModel):
    id: uuid.UUID
    title: str
    occurrence: datetime
    description: str | None
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True # Allows the schema to be created from a SQLAlchemy model
```

### Step 2: Write the Repository (`app/repositories/`)
The repository layer is responsible for all direct database interactions.

-   **Why?**: It abstracts the database logic, making your services independent of the data source and easier to test (you can mock the repository).

**Example (`app/repositories/event_repository.py`):**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.event import Event
from app.schemas.event import EventCreate
import uuid

class EventRepository:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_event(self, event_data: EventCreate, owner_id: uuid.UUID) -> Event:
        new_event = Event(
            title=event_data.title,
            occurrence=event_data.occurrence,
            description=event_data.description,
            owner_id=owner_id
        )
        self.db.add(new_event)
        await self.db.commit()
        await self.db.refresh(new_event)
        return new_event
```

### Step 3: Implement the Service (`app/services/`)
The service layer contains the core business logic. It coordinates repositories and other services to fulfill a use case.

-   **Why?**: It keeps business logic separate from the HTTP transport layer (the API endpoint), making it reusable and easier to reason about.

**Example (`app/services/event_service.py`):**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreate
from app.models.user import User
from app.models.event import Event

class EventService:
    def __init__(self, db_session: AsyncSession):
        self.repo = EventRepository(db_session)

    async def create_new_event(self, event_data: EventCreate, current_user: User) -> Event:
        # Business logic can be added here, e.g., checking for overlapping events
        # or enforcing limits on the number of events a user can create.
        
        new_event = await self.repo.create_event(event_data, owner_id=current_user.id)
        
        # You could also trigger other services here, like sending a notification.
        
        return new_event
```

### Step 4: Create the API Endpoint (`app/api/v1/endpoints/`)
This is the final layer. It handles the HTTP request and response.

-   **Why?**: This layer should be "thin". Its only job is to parse the request, call the appropriate service, handle HTTP-specific exceptions, and format the response.

**Example (`app/api/v1/endpoints/events.py`):**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.schemas.event import EventCreate, EventRead
from app.services.event_service import EventService
from app.utils.dependencies import get_db, get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post(
    "/",
    response_model=EventRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new event",
    description="Creates a new event for the authenticated user."
)
async def create_event_endpoint(
    event_in: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Endpoint to create a new event.
    - **title**: The title of the event.
    - **occurrence**: The date and time the event occurs.
    - **description**: An optional description for the event.
    """
    try:
        service = EventService(db)
        new_event = await service.create_new_event(event_data=event_in, current_user=current_user)
        return new_event
    except Exception as e:
        # In a real app, you would have more specific exception handling
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )
```

---

## 4. Phase 3: Testing

Thorough testing is non-negotiable. Tests should cover business logic, database interactions, and the HTTP interface.

### 4.1 Write Unit & Integration Tests (`tests/`)
-   **Unit Tests**: Test individual components in isolation (e.g., test the `EventService` by mocking the `EventRepository`).
-   **Integration Tests**: Test the endpoint from the outside in, using a test client and a test database.

**Example Integration Test (`tests/api/v1/test_event_endpoints.py`):**
```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

@pytest.mark.asyncio
async def test_create_event_success(
    client: AsyncClient, 
    test_user_auth_headers: dict[str, str]
):
    # Arrange
    event_data = {
        "title": "My Test Event",
        "occurrence": "2024-10-20T10:00:00Z",
        "description": "This is a test."
    }
    
    # Act
    response = await client.post(
        "/api/v1/events/", 
        json=event_data, 
        headers=test_user_auth_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == event_data["title"]
    assert "id" in data
```

---

## 5. Phase 4: Finalization

### 5.1 Documentation and Security
-   **API Docs**: Thanks to FastAPI, Pydantic, and good docstrings, your API documentation at `/docs` is already mostly complete. Review it to ensure clarity.
-   **Rate Limiting**: Apply rate limiting if the endpoint is sensitive to abuse.
-   **Permissions**: Double-check that your dependencies (`get_current_active_user`) correctly enforce the required permission levels.

### 5.2 Logging
-   Integrate structured logging within your services to record important events, errors, and access patterns. This is crucial for debugging and monitoring.

By following this guide, you will produce high-quality, professional-grade endpoints that are a valuable and maintainable asset to the project. 