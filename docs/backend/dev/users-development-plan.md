# Professional User Management API Development Plan

## 1. Overview

This document provides a comprehensive, phased development plan for implementing the user profile and security management backend for the UCC Event Manager. It translates the requirements from the PRD, API specs, and security documents into a concrete, step-by-step roadmap for developers.

The goal is to build a secure and robust set of endpoints for users to manage their own profile, change their password, and view/revoke active sessions, following the project's established architecture (`docs/backend/endpoint-creation-guide.md`).

**User Stories Covered:**

- **US-101 (Implicit)**: As a user, I want to view my profile information to ensure it is correct.
- **US-102 (Implicit)**: As a user, I want to update my profile information (e.g., my full name) to keep it current.
- **US-103 (Implicit)**: As a user, I want to change my password to keep my account secure.
- **US-104 (Implicit)**: As a user, I want to view my active sessions to monitor for suspicious activity.
- **US-105 (Implicit)**: As a user, I want to revoke a specific session if I lose a device or don't recognize it.

---

## Phase 1: Schemas & Data Structures

**Objective**: Define the Pydantic schemas that enforce the API contract for all user management operations, ensuring type safety and clear validation.

### Task 1.1: Define User Profile Schemas

- **File**: `app/schemas/user.py`
- **Action**: Create or refine Pydantic schemas for user profile data.
- **Details**:
  - **`UserRead`**: The response model for `GET /users/me`.
    - `id`: `uuid.UUID`
    - `email`: `pydantic.EmailStr`
    - `full_name`: `str`
    - `mfa_enabled`: `bool`
    - `is_active`: `bool`
    - `created_at`: `datetime`
    - `updated_at`: `datetime`
  - **`UserUpdate`**: The request model for `PATCH /users/me`.
    - `full_name`: `str | None` (Field validation: min_length=1, max_length=255)
    - `email`: `pydantic.EmailStr | None` (Optional, allows for future extension)

### Task 1.2: Define Password Management Schema

- **File**: `app/schemas/password.py`
- **Action**: Create a schema for the password change request.
- **Details**:
  - **`PasswordChange`**:
    - `current_password`: `str`
    - `new_password`: `str` (Field validation: add strong password validator as per `security.md`)

### Task 1.3: Define Session Management Schemas

- **File**: `app/schemas/token.py`
- **Action**: Create schemas for listing user sessions (active refresh tokens).
- **Details**:
  - **`SessionRead`**: A schema for a single session.
    - `id`: `uuid.UUID` (The `refresh_tokens.id` field)
    - `ip_address`: `str | None` (Note: Requires adding this column to the `refresh_tokens` table)
    - `user_agent`: `str | None` (Note: Requires adding this column to the `refresh_tokens` table)
    - `created_at`: `datetime`
    - `expires_at`: `datetime`
  - **`PaginatedSessionRead`**: A schema for paginated session responses.
    - `total`: `int`
    - `limit`: `int`
    - `offset`: `int`
    - `data`: `list[SessionRead]`

---

## Phase 2: Data Access Layer (Repository)

**Objective**: Implement the database interaction logic for the `users` and `refresh_tokens` tables.

### Task 2.1: Enhance User Repository

- **File**: `app/repositories/user_repository.py`
- **Action**: Ensure the `UserRepository` supports all necessary user update operations.
- **Details**:
  - Verify or implement `update(db_user: User, user_data: dict) -> User`: A generic update method that can handle partial updates for `full_name`, `email`, or `password_hash`.

### Task 2.2: Implement Token Repository

- **File**: `app/repositories/token_repository.py`
- **Action**: Create a new `TokenRepository` to handle data access for `refresh_tokens`.
- **Details**:
  - **`get_by_id(token_id: UUID) -> RefreshToken | None`**: Fetches a refresh token by its primary key.
  - **`get_all_by_user_id(user_id: UUID, offset: int, limit: int) -> tuple[list[RefreshToken], int]`**: Fetches a paginated list of non-revoked refresh tokens for a user.
  - **`revoke(db_token: RefreshToken) -> RefreshToken`**: Marks a token as `is_revoked=True`.
  - **`revoke_all_for_user(user_id: UUID) -> None`**: Marks all non-revoked tokens for a user as revoked (useful for after password changes).

---

## Phase 3: Business Logic (Service)

**Objective**: Create the `UserService` to orchestrate repository calls and enforce business rules, including security checks.

### Task 3.1: Implement User Service

- **File**: `app/services/user_service.py`
- **Action**: Create or enhance the `UserService` class.
- **Details**:
  - **`update_profile(current_user: User, update_data: UserUpdate) -> User`**:
    1. Calls `user_repository.update`.
    2. Logs the profile update event.
  - **`change_password(current_user: User, password_data: PasswordChange) -> None`**:
    1. **Security Check**: Verify `password_data.current_password` using `pwd_context.verify`. Raise `HTTPException` (400) on failure.
    2. Hash the `new_password` using `pwd_context.hash`.
    3. Update the user's `password_hash` via the repository.
    4. **Crucial Security Step**: Call `token_repository.revoke_all_for_user` to revoke all active sessions, forcing a re-login on all other devices.
    5. Log the "password_changed" security event.
  - **`get_sessions(current_user: User, ...) -> tuple[list[RefreshToken], int]`**:
    1. Calls `token_repository.get_all_by_user_id`.
  - **`revoke_session(current_user: User, session_id: UUID) -> None`**:
    1. Call `token_repository.get_by_id` to fetch the session.
    2. **Crucial Security Check**: If the session is not found or `session.user_id != current_user.id`, raise `HTTPException` (404).
    3. Call `token_repository.revoke`.
    4. Log the "session_revoked" security event.

---

## Phase 4: API Endpoint Implementation

**Objective**: Create the public-facing API endpoints in `users.py`, delegating all logic to the `UserService`.

### Task 4.1: Get User Profile (`GET /users/me`)

- **File**: `app/api/v1/endpoints/users.py`
- **Action**: Implement the `get_current_user_profile` endpoint.
- **Details**:
  - **Path**: `/me`
  - **Method**: `GET`
  - **Response Model**: `UserRead`
  - **Dependencies**: `get_current_active_user`
  - **Logic**: Simply return the `current_user` object. FastAPI will handle serialization.

### Task 4.2: Update User Profile (`PATCH /users/me`)

- **File**: `app/api/v1/endpoints/users.py`
- **Action**: Implement the `update_current_user_profile` endpoint.
- **Details**:
  - **Path**: `/me`
  - **Method**: `PATCH`
  - **Response Model**: `UserRead`
  - **Dependencies**: `get_db`, `get_current_active_user`
  - **Logic**:
    1. Instantiate `UserService`.
    2. Call `service.update_profile`.
    3. Return the updated user.

### Task 4.3: Change Password (`POST /users/me/change-password`)

- **File**: `app/api/v1/endpoints/users.py`
- **Action**: Implement the `change_current_user_password` endpoint.
- **Details**:
  - **Path**: `/me/change-password`
  - **Method**: `POST`
  - **Response**: `200 OK` with a JSON message.
  - **Dependencies**: `get_db`, `get_current_active_user`
  - **Logic**:
    1. Instantiate `UserService`.
    2. Call `service.change_password`.
    3. Return `{"message": "Password changed successfully"}`.

### Task 4.4: List User Sessions (`GET /users/me/sessions`)

- **File**: `app/api/v1/endpoints/users.py`
- **Action**: Implement the `list_current_user_sessions` endpoint.
- **Details**:
  - **Path**: `/me/sessions`
  - **Method**: `GET`
  - **Response Model**: `PaginatedSessionRead`
  - **Dependencies**: `get_db`, `get_current_active_user`, pagination query params.
  - **Logic**:
    1. Instantiate `UserService`.
    2. Call `service.get_sessions`.
    3. Format and return the paginated response.

### Task 4.5: Delete User Session (`DELETE /users/me/sessions/{session_id}`)

- **File**: `app/api/v1/endpoints/users.py`
- **Action**: Implement the `delete_user_session` endpoint.
- **Details**:
  - **Path**: `/me/sessions/{session_id}`
  - **Method**: `DELETE`
  - **Response Status Code**: `204 NO CONTENT`
  - **Dependencies**: `get_db`, `get_current_active_user`
  - **Logic**:
    1. Instantiate `UserService`.
    2. Call `service.revoke_session`.
    3. Return an empty response with a 204 status code.

---

## Phase 5: Testing

**Objective**: Write comprehensive integration tests to ensure all user management endpoints are correct, secure, and robust.

### Task 5.1: Write Integration Tests

- **File**: `tests/api/v1/test_user_endpoints.py`
- **Action**: Create integration tests for every endpoint and scenario.
- **Details**:
  - **Success Cases**:
    - Test `GET /users/me` returns the correct profile.
    - Test `PATCH /users/me` successfully updates `full_name`.
    - Test `POST /users/me/change-password` with correct old password works and returns 200.
    - Test `GET /users/me/sessions` returns a list of active sessions.
    - Test `DELETE /users/me/sessions/{session_id}` works and returns 204.
  - **Failure & Security Cases**:
    - **Authorization**: Test all endpoints fail with `401 UNAUTHORIZED` if no token is provided.
    - **Permissions**: Create two users (A and B). Create a session for User A. Logged in as User B, attempt to `DELETE` User A's session and assert a `404 NOT FOUND`.
    - **Validation**: Test `POST /users/me/change-password` with an incorrect `current_password` and assert `400 BAD REQUEST`. Test with a weak `new_password` and assert `422 UNPROCESSABLE ENTITY`.
    - **Not Found**: Test `DELETE /users/me/sessions/{session_id}` with a non-existent UUID and assert `404 NOT FOUND`.

---

## Phase 6: Finalization & Hardening

**Objective**: Ensure the endpoints are documented, secure, and production-ready.

- **API Documentation Review**:
  - Start the application and navigate to `/docs`.
  - Add `summary`, `description`, and `tags=["Users"]` to the endpoint decorators in `users.py` to ensure the documentation is clear and well-organized.
- **Rate Limiting**:
  - Apply rate limits to the user management endpoints. A stricter limit should be applied to `POST /users/me/change-password` (e.g., "5/hour") compared to profile updates.
- **Logging**:
  - Integrate structured logging (`structlog`) within the `UserService` to log key security events: `profile_updated`, `password_changed`, `session_revoked`. Each log should include `user_id` and the client's IP address.
- **Code Review**:
  - Conduct a peer review focused on security (password verification, session ownership checks), correctness, and adherence to project standards. 