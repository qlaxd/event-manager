# Professional Helpdesk API Development Plan

## 1. Overview
This document provides a comprehensive, phased development plan for implementing the helpdesk backend for the UCC Event Manager. It translates the requirements from the PRD, API specs, and architectural documents into a step-by-step roadmap for developers.

The goal is to build secure and robust endpoints for a chatbot that can answer user questions and escalate to a human agent, as well as bonus voice-based interaction capabilities. This plan follows the project's established architecture (`docs/backend/endpoint-creation-guide.md`).

**User Stories Covered:**
- **US-008**: Use the helpdesk chatbot
- **US-009**: Use the voice-based helpdesk (bonus)

---

## Phase 1: Models, Schemas, and Service Clients

**Objective**: Define the data structures, API contracts, and external service abstractions required for the helpdesk feature.

### Task 1.1: Database Models
-   **File**: `app/models/helpdesk.py`
-   **Action**: Create SQLAlchemy models to store conversation state.
-   **Details**:
    -   **`ChatSession` Model**:
        -   `id`: `UUID` (Primary Key)
        -   `user_id`: `UUID` (Foreign Key to `users.id`, non-nullable)
        -   `is_active`: `Boolean` (Default `True`, to track open/closed sessions)
        -   `created_at`, `updated_at`: `DateTime`
    -   **`ChatMessage` Model**:
        -   `id`: `UUID` (Primary Key)
        -   `session_id`: `UUID` (Foreign Key to `chat_sessions.id`, non-nullable)
        -   `sender`: `String` (Enum-like: "USER" or "BOT")
        -   `content`: `Text` (The message itself)
        -   `metadata`: `JSONB` (Optional, for storing confidence scores, etc.)
        -   `created_at`: `DateTime`

### Task 1.2: Pydantic Schemas
-   **File**: `app/schemas/helpdesk.py`
-   **Action**: Define Pydantic schemas for API request/response validation.
-   **Details**:
    -   `ChatMessageRead`: Response schema for a single message.
    -   `ChatSessionRead`: Response schema for a session.
    -   `ChatRequest`: For `POST /helpdesk/chat` (`message: str`, `session_id: UUID`).
    -   `ChatResponse`: For `POST /helpdesk/chat` (`response: str`, `session_id: UUID`, `confidence: float`, `escalation_suggested: bool`, `quick_replies: list[str]`).
    -   `EscalateRequest`: For `POST /helpdesk/escalate` (`session_id: UUID`, `reason: str`, `message: str`).
    -   `EscalateResponse`: For `POST /helpdesk/escalate` (`ticket_id: str`, `message: str`, `estimated_wait_time: str`).
    -   `PaginatedChatMessages`: For `GET /helpdesk/sessions/{session_id}/messages` (`total: int`, `limit: int`, `offset: int`, `data: list[ChatMessageRead]`).

### Task 1.3: Chatbot Service Client
-   **File**: `app/clients/chatbot_client.py`
-   **Action**: Abstract the communication with the external chatbot service (e.g., Rasa).
-   **Details**:
    -   Create a `ChatbotClient` class.
    -   Implement an `async def get_response(self, message: str, session_id: str) -> dict:` method.
        -   This method will use `httpx.AsyncClient` to `POST` to the Rasa server's webhook.
        -   It should handle connection errors and non-200 responses gracefully.
    -   Add `CHATBOT_URL` to `app/core/config.py` and `.env.example`.

---

## Phase 2: Data Access Layer (Repository)

**Objective**: Implement the database interaction logic for helpdesk models.

### Task 2.1: Implement Helpdesk Repositories
-   **File**: `app/repositories/helpdesk_repository.py`
-   **Action**: Create repository classes for `ChatSession` and `ChatMessage`.
-   **Details**:
    -   **`ChatSessionRepository`**:
        -   `create(user_id: UUID) -> ChatSession`
        -   `get_by_id(session_id: UUID) -> ChatSession | None`
        -   `deactivate(db_session: ChatSession) -> ChatSession`
    -   **`ChatMessageRepository`**:
        -   `create(session_id: UUID, sender: str, content: str, metadata: dict | None) -> ChatMessage`
        -   `get_by_session_id(session_id: UUID, offset: int, limit: int) -> tuple[list[ChatMessage], int]`

---

## Phase 3: Business Logic (Service)

**Objective**: Orchestrate repository and client calls to implement the core helpdesk logic, including security checks.

### Task 3.1: Implement Helpdesk Service
-   **File**: `app/services/helpdesk_service.py`
-   **Action**: Create the `HelpdeskService` class.
-   **Details**:
    -   **`_get_session_and_verify_ownership(session_id: UUID, current_user: User) -> ChatSession`**:
        -   A private helper to fetch a session and ensure `session.user_id == current_user.id`.
        -   Raises `HTTPException(404, "Session not found")` if not found or owner mismatch to prevent leaking information.
    -   **`create_session(current_user: User) -> ChatSession`**: Creates a new session for the user.
    -   **`process_chat_message(request: ChatRequest, current_user: User) -> ChatResponse`**:
        1.  Use the helper to get and verify the session.
        2.  Save the user's message via `ChatMessageRepository`.
        3.  Call `chatbot_client.get_response`.
        4.  Save the bot's response via `ChatMessageRepository`.
        5.  Return the formatted `ChatResponse`.
    -   **`escalate_to_human(request: EscalateRequest, current_user: User) -> EscalateResponse`**:
        1.  Use the helper to get and verify the session.
        2.  Log the escalation request. For now, this can generate a mock ticket ID.
        3.  Deactivate the session via `ChatSessionRepository`.
        4.  Return a mock `EscalateResponse`.
    -   **`get_chat_history(session_id: UUID, current_user: User, offset: int, limit: int) -> PaginatedChatMessages`**:
        1.  Use the helper to get and verify the session.
        2.  Fetch message history via `ChatMessageRepository`.
        3.  Return the formatted `PaginatedChatMessages`.

---

## Phase 4: API Endpoint Implementation

**Objective**: Expose the helpdesk service logic via "thin" FastAPI endpoints.

### Task 4.1: Implement Helpdesk Endpoints
-   **File**: `app/api/v1/endpoints/helpdesk.py`
-   **Action**: Implement the five core chat-related endpoints.
-   **Details**:
    -   **`POST /sessions`**: Creates a new chat session. `Response Model: ChatSessionRead`, `Status: 201`.
    -   **`POST /chat`**: Sends a message. `Response Model: ChatResponse`.
    -   **`POST /escalate`**: Escalates a session. `Response Model: EscalateResponse`.
    -   **`GET /sessions/{session_id}/messages`**: Gets history. `Response Model: PaginatedChatMessages`.
    -   **`DELETE /sessions/{session_id}`**: Deactivates a session. `Status: 204`.
    -   All endpoints must depend on `get_current_active_user`.

---

## Phase 5: Testing

**Objective**: Write comprehensive tests to ensure functionality, security, and correctness.

### Task 5.1: Write Integration Tests
-   **File**: `tests/api/v1/test_helpdesk_endpoints.py`
-   **Action**: Test all endpoints and scenarios.
-   **Details**:
    -   **Mocking**: Use `pytest-mock` to mock the `ChatbotClient` and control its responses for predictable tests.
    -   **Success Cases**: Test the full lifecycle: create session, send messages, get history, escalate/delete.
    -   **Security Cases**:
        -   Verify all endpoints fail with `401` if unauthenticated.
        -   Create two users (A and B). Have A create a session. Verify that B cannot access (`GET`, `POST`, `DELETE`) A's session, receiving a `404` for each attempt.
    -   **Validation Cases**: Test invalid input (e.g., bad session UUID, missing fields) and assert `422` responses.

---

## Phase 6: Bonus - Voice Helpdesk

**Objective**: Implement the bonus voice-based helpdesk functionality.

### Task 6.1: Voice Schemas and Client
-   **File (`schemas`)**: Add `VoiceSessionResponse`, `VoiceProcessRequest`, `VoiceProcessResponse` to `app/schemas/helpdesk.py`.
-   **File (`clients`)**: Create `app/clients/voice_client.py`.
    -   Abstracts a Speech-to-Text (STT) and Text-to-Speech (TTS) provider (e.g., Twilio, Google Speech).
    -   Add configuration to `app/core/config.py`.

### Task 6.2: Extend Helpdesk Service
-   **File**: `app/services/helpdesk_service.py`
-   **Action**: Add methods for voice interactions.
-   **Details**:
    -   **`start_voice_session(...)`**: Logic to initiate a voice session, possibly returning a WebSocket URL or session token for a voice provider.
    -   **`process_voice_message(...)`**:
        1.  Use `voice_client` to perform STT on incoming audio data.
        2.  Feed the transcribed text into the existing `process_chat_message` logic.
        3.  Use `voice_client` to perform TTS on the text response.
        4.  Return the response, including the audio data of the reply.

### Task 6.3: Voice Endpoints & Testing
-   **File (`endpoints`)**: Implement `POST /helpdesk/voice/session` and `POST /helpdesk/voice/process`.
-   **File (`tests`)**: Add tests for the voice endpoints, mocking the `VoiceClient`.

---

## Phase 7: Finalization & Hardening

**Objective**: Ensure the endpoints are production-ready.

-   **API Documentation**: Review and enhance the auto-generated OpenAPI docs at `/docs`. Add clear summaries and descriptions for each endpoint.
-   **Rate Limiting**: Apply appropriate rate limits using `slowapi` to the helpdesk endpoints to prevent abuse.
-   **Logging**: Integrate structured logging (`structlog`) within the `HelpdeskService` to log key actions (e.g., "Session created", "Chat escalated") including `user_id` and `session_id`.

By executing this plan, your team will systematically build a secure, maintainable, and fully-featured API for the helpdesk system. 