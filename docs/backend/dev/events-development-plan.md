# Professional Event Management API Development Plan

## 1. Overview
This document provides a comprehensive, phased development plan for implementing the event management backend for the UCC Event Manager. It translates the requirements from the PRD, API specs, and data model into a concrete, step-by-step roadmap for developers.

The goal is to build a secure and robust set of CRUD (Create, Read, Update, Delete) endpoints for user-specific events, following the project's established architecture (`docs/backend/endpoint-creation-guide.md`).

**User Stories Covered:**
- **US-004**: Create a new event
- **US-005**: View my events
- **US-006**: Update event description
- **US-007**: Delete an event

---

## Phase 1: Schemas & Data Structures

**Objective**: Define the Pydantic schemas that enforce the API contract for all event-related operations.

### Task 1.1: Define Event Schemas
-   **File**: `app/schemas/event.py`
-   **Action**: Create and refine Pydantic schemas for event data.
-   **Details**:
    -   **`EventBase`**: A base schema with common fields.
        -   `title`: `str` (Field validation: min_length=1, max_length=255)
        -   `occurrence`: `datetime`
        -   `description`: `str | None` (Field validation: max_length=10000)
    -   **`EventCreate`**: Schema for creating an event. Inherits from `EventBase`.
    -   **`EventUpdate`**: Schema for updating an event. This is specific to the requirement that only the description can be changed.
        -   `description`: `str | None` (Field validation: max_length=10000)
    -   **`EventRead`**: The response model for reading one or more events. Inherits from `EventBase`.
        -   `id`: `uuid.UUID`
        -   `user_id`: `uuid.UUID`
        -   `created_at`: `datetime`
        -   `updated_at`: `datetime`
    -   **`PaginatedEventRead`**: A schema for paginated responses (`GET /events`).
        -   `total`: `int`
        -   `limit`: `int`
        -   `offset`: `int`
        -   `data`: `list[EventRead]`

---

## Phase 2: Data Access Layer (Repository)

**Objective**: Implement the database interaction logic for the `events` table, ensuring all queries are efficient and secure.

### Task 2.1: Implement Event Repository
-   **File**: `app/repositories/event_repository.py`
-   **Action**: Create the `EventRepository` class with methods for all CRUD operations.
-   **Details**:
    -   **`create(event_data: EventCreate, user_id: UUID) -> Event`**: Creates a new event record.
    -   **`get_by_id(event_id: UUID) -> Event | None`**: Fetches a single event by its primary key.
    -   **`get_all_by_user_id(user_id: UUID, offset: int, limit: int, sort: str, order: str) -> tuple[list[Event], int]`**: Fetches a paginated, sorted list of events for a specific user. It should return both the list of events and the total count for that user.
    -   **`update(db_event: Event, event_data: EventUpdate) -> Event`**: Updates an existing event record in the database.
    -   **`delete(db_event: Event) -> None`**: Deletes an event record from the database.

---

## Phase 3: Business Logic (Service)

**Objective**: Create the `EventService` to orchestrate repository calls and enforce business rules, most importantly resource ownership.

### Task 3.1: Implement Event Service
-   **File**: `app/services/event_service.py`
-   **Action**: Create the `EventService` class. This layer is critical for security, as it will check that a user is authorized to perform an action on an event.
-   **Details**:
    -   **`create_event(event_data: EventCreate, current_user: User) -> Event`**:
        1.  Calls `event_repository.create`.
    -   **`get_user_events(current_user: User, ...) -> tuple[list[Event], int]`**:
        1.  Calls `event_repository.get_all_by_user_id` using the `current_user.id`.
    -   **`get_event_by_id(event_id: UUID, current_user: User) -> Event`**:
        1.  Calls `event_repository.get_by_id`.
        2.  **Crucial Security Check**: If the event is not found, or if `event.user_id != current_user.id`, raise an `HTTPException` with status `404 NOT FOUND`. This prevents leaking information about the existence of events belonging to other users.
    -   **`update_event(event_id: UUID, event_data: EventUpdate, current_user: User) -> Event`**:
        1.  First, call `get_event_by_id` which includes the ownership check.
        2.  If authorized, call `event_repository.update`.
    -   **`delete_event(event_id: UUID, current_user: User) -> None`**:
        1.  First, call `get_event_by_id` to get the event and verify ownership.
        2.  If authorized, call `event_repository.delete`.

---

## Phase 4: API Endpoint Implementation

**Objective**: Create the public-facing API endpoints in `events.py`, keeping them "thin" by delegating all logic to the `EventService`.

### Task 4.1: Create New Event (`POST /events`)
-   **File**: `app/api/v1/endpoints/events.py`
-   **Action**: Implement the `create_event` endpoint.
-   **Details**:
    -   **Path**: `/`
    -   **Method**: `POST`
    -   **Response Model**: `EventRead`
    -   **Status Code**: `201 CREATED`
    -   **Dependencies**: `get_db`, `get_current_active_user`
    -   **Logic**:
        1.  Instantiate `EventService`.
        2.  Call `service.create_event` with the request body and `current_user`.
        3.  Return the newly created event.

### Task 4.2: List User Events (`GET /events`)
-   **File**: `app/api/v1/endpoints/events.py`
-   **Action**: Implement the `list_events` endpoint.
-   **Details**:
    -   **Path**: `/`
    -   **Method**: `GET`
    -   **Response Model**: `PaginatedEventRead`
    -   **Dependencies**: `get_db`, `get_current_active_user`
    -   **Query Parameters**: As per `api-specs.md`: `limit`, `offset`, `sort`, `order`. Add default values and validation (e.g., `Query(ge=0)`, `Query(le=100)`).
    -   **Logic**:
        1.  Instantiate `EventService`.
        2.  Call `service.get_user_events`, passing the `current_user` and query parameters.
        3.  Format the result into the `PaginatedEventRead` schema.

### Task 4.3: Get Single Event (`GET /events/{event_id}`)
-   **File**: `app/api/v1/endpoints/events.py`
-   **Action**: Implement the `get_event` endpoint.
-   **Details**:
    -   **Path**: `/{event_id}`
    -   **Method**: `GET`
    -   **Response Model**: `EventRead`
    -   **Dependencies**: `get_db`, `get_current_active_user`
    -   **Logic**:
        1.  Instantiate `EventService`.
        2.  Call `service.get_event_by_id`, which handles the 404/permission check.
        3.  Return the event.

### Task 4.4: Update Event (`PATCH /events/{event_id}`)
-   **File**: `app/api/v1/endpoints/events.py`
-   **Action**: Implement the `update_event` endpoint.
-   **Details**:
    -   **Path**: `/{event_id}`
    -   **Method**: `PATCH`
    -   **Response Model**: `EventRead`
    -   **Dependencies**: `get_db`, `get_current_active_user`
    -   **Logic**:
        1.  Instantiate `EventService`.
        2.  Call `service.update_event` with the `event_id`, request body (`EventUpdate`), and `current_user`. The service handles ownership checks.
        3.  Return the updated event.

### Task 4.5: Delete Event (`DELETE /events/{event_id}`)
-   **File**: `app/api/v1/endpoints/events.py`
-   **Action**: Implement the `delete_event` endpoint.
-   **Details**:
    -   **Path**: `/{event_id}`
    -   **Method**: `DELETE`
    -   **Response Status Code**: `204 NO CONTENT`
    -   **Dependencies**: `get_db`, `get_current_active_user`
    -   **Logic**:
        1.  Instantiate `EventService`.
        2.  Call `service.delete_event` with `event_id` and `current_user`. The service handles ownership checks.
        3.  Return an empty response with a 204 status code.

---

## Phase 5: Testing

**Objective**: Write comprehensive integration tests to ensure all event endpoints are functionally correct, secure, and performant.

### Task 5.1: Write Integration Tests
-   **File**: `tests/api/v1/test_event_endpoints.py`
-   **Action**: Create integration tests for every endpoint and scenario.
-   **Details**:
    -   **Fixtures**: Use `test_user` and `test_client` fixtures from `conftest.py`. Create fixtures to pre-populate events for test users.
    -   **Success Cases**:
        -   Test creating an event successfully (`POST /events`).
        -   Test listing events, including pagination and sorting (`GET /events`).
        -   Test getting a single event (`GET /events/{event_id}`).
        -   Test updating an event description (`PATCH /events/{event_id}`).
        -   Test deleting an event (`DELETE /events/{event_id}`).
    -   **Failure & Security Cases**:
        -   **Authorization**: Test that unauthenticated requests to any event endpoint fail with a `401 UNAUTHORIZED`.
        -   **Permissions**: Create two users (User A, User B). Create an event for User A. As User B, attempt to `GET`, `PATCH`, and `DELETE` User A's event. Assert that all attempts fail with `404 NOT FOUND`.
        -   **Validation**: Test creating an event with invalid data (e.g., missing title, title too long) and assert a `422 UNPROCESSABLE ENTITY` response.
        -   **Not Found**: Test `GET`, `PATCH`, `DELETE` with a non-existent `event_id` and assert a `404 NOT FOUND`.

---

## Phase 6: Finalization & Hardening

**Objective**: Ensure the endpoints are production-ready.

-   **API Documentation Review**:
    -   Start the application and navigate to `/docs`.
    -   Review the auto-generated OpenAPI documentation for all event endpoints.
    -   Add `summary` and `description` parameters to the endpoint decorators in `events.py` to ensure the documentation is clear and helpful.
-   **Rate Limiting**:
    -   In consultation with the security requirements (`security.md`), apply appropriate rate limits to the event endpoints using `slowapi`. A general limit for CRUD operations is a good starting point.
-   **Logging**:
    -   Integrate structured logging (`structlog`) within the `EventService` to log key actions (e.g., "Event created", "Event deleted") including `user_id` and `event_id`. Avoid logging sensitive data from the event itself.
-   **Code Review**:
    -   Conduct a peer review focused on security (especially the ownership checks in the service layer), correctness, and adherence to the project's coding standards.

By executing this plan, your team will systematically build a secure, maintainable, and fully-featured API for event management. 