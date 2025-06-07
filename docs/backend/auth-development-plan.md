# Professional Authentication API Development Plan

## 1. Overview
This document provides a comprehensive, phased development plan for implementing the authentication and user management backend for the UCC Event Manager. It translates the requirements from the PRD, API specs, and security documents into a concrete, step-by-step roadmap for developers.

The goal is to build a secure, robust, and professional authentication system featuring JWT, password reset, and Multi-Factor Authentication (MFA), following the project's established architecture.

---

## Phase 1: Core Foundation & Security Setup

**Objective**: Establish the fundamental components required for all security operations.

### Task 1.1: Configuration
-   **File**: `app/core/config.py`
-   **Action**: Extend the Pydantic settings class to include all authentication-related configurations.
-   **Details**:
    -   `SECRET_KEY`: For signing non-JWT tokens (e.g., password reset).
    -   `ACCESS_TOKEN_EXPIRE_MINUTES`: e.g., `30`
    -   `REFRESH_TOKEN_EXPIRE_DAYS`: e.g., `7`
    -   `JWT_ALGORITHM`: e.g., `"RS256"`
    -   `JWT_PRIVATE_KEY_PATH`: Path to `keys/jwt-private.pem`
    -   `JWT_PUBLIC_KEY_PATH`: Path to `keys/jwt-public.pem`
    -   **Update `.env.example`** with these new variables.

### Task 1.2: Cryptographic Utilities
-   **File**: `app/core/security.py`
-   **Actions**: Implement core cryptographic functions.
-   **Details**:
    -   **Password Hashing**:
        -   Create a `pwd_context` using `passlib.context.CryptContext` with `bcrypt`.
        -   Implement `verify_password(plain_password, hashed_password) -> bool`.
        -   Implement `get_password_hash(password) -> str`.
    -   **JWT Handling**:
        -   Load the RSA private and public keys from the paths defined in the config.
        -   Implement `create_access_token(data: dict) -> str`.
        -   Implement `create_refresh_token(data: dict) -> str`.
        -   Implement `verify_token(token: str) -> dict | None`: Decodes the token using the public key and handles exceptions (`PyJWTError`).

### Task 1.3: Database Models
-   **Files**: `app/models/user.py`, `app/models/token.py`
-   **Actions**: Define the SQLAlchemy models for users and tokens.
-   **Details**:
    -   **`User` Model (`user.py`)**:
        -   Fields: `id` (UUID), `email` (String, unique, index), `hashed_password` (String), `full_name` (String, nullable), `is_active` (Boolean, default `True`).
    -   **`RefreshToken` Model (`token.py`)**:
        -   This is crucial for secure logout (revocation).
        -   Fields: `id`, `user_id` (ForeignKey), `token` (String, index), `expires_at` (DateTime), `is_revoked` (Boolean, default `False`).

---

## Phase 2: User Login & Token Generation (`POST /auth/token`)

**Objective**: Implement the primary user authentication endpoint.

### Task 2.1: Schemas
-   **File**: `app/schemas/token.py`
-   **Actions**: Define Pydantic schemas for token-related data.
-   **Details**:
    -   `Token`: The response model for the login endpoint. Fields: `access_token`, `refresh_token`, `token_type`.
    -   `TokenPayload`: The data encoded within the JWT. Fields: `sub` (subject, e.g., user ID), `exp`.

### Task 2.2: Repository
-   **File**: `app/repositories/user_repository.py`
-   **Action**: Create a method to fetch a user from the database.
-   **Details**:
    -   Implement `get_by_email(email: str) -> User | None`.

### Task 2.3: Authentication Service
-   **File**: `app/services/auth_service.py`
-   **Action**: Create the core authentication logic.
-   **Details**:
    -   Implement `authenticate_user(email: str, password: str) -> User | None`:
        1.  Calls `user_repository.get_by_email`.
        2.  If user not found or inactive, return `None`.
        3.  Calls `security.verify_password`.
        4.  If password matches, return the `user` object. Otherwise, return `None`.
    -   Implement a method to save and manage refresh tokens in the database.

### Task 2.4: Endpoint Implementation
-   **File**: `app/api/v1/endpoints/auth.py`
-   **Action**: Create the `/token` endpoint.
-   **Details**:
    -   Use FastAPI's `OAuth2PasswordRequestForm` dependency (`form_data`).
    -   Call `auth_service.authenticate_user(email=form_data.username, password=form_data.password)`.
    -   If authentication fails, raise `HTTPException` with status `401 UNAUTHORIZED`.
    -   If successful, call `security.create_access_token` and `security.create_refresh_token`.
    -   Store the refresh token in the database via the service.
    -   Return the tokens using the `schemas.Token` response model.

---

## Phase 3: Endpoint Protection & User Profile

**Objective**: Create the dependency that protects endpoints and build the first protected route.

### Task 3.1: "Get Current User" Dependency
-   **File**: `app/utils/dependencies.py`
-   **Action**: Implement the primary dependency for endpoint authorization.
-   **Details**:
    -   Define an `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")`.
    -   Create `get_current_active_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User`:
        1.  Calls `security.verify_token` to decode the JWT.
        2.  Handles token validation errors (e.g., expired, invalid) by raising a 401 HTTPException.
        3.  Extracts the user ID from the token payload (`sub` claim).
        4.  Fetches the user from the database via `user_repository`.
        5.  If user not found or is inactive, raise a 401 HTTPException.
        6.  Returns the `user` object.

### Task 3.2: User Profile Endpoint (`GET /users/me`)
-   **File**: `app/api/v1/endpoints/users.py`
-   **Action**: Create an endpoint that uses the new dependency.
-   **Details**:
    -   Create a `GET /me` endpoint.
    -   Protect it by adding `current_user: User = Depends(get_current_active_user)` to the function signature.
    -   The endpoint simply returns the `current_user` object. This validates the entire auth flow.

---

## Phase 4: Password Reset Flow

**Objective**: Implement a secure, token-based password reset mechanism.

### Task 4.1: Database Model
-   **File**: `app/models/token.py`
-   **Action**: Create a `PasswordResetToken` model.
-   **Details**:
    -   Fields: `id`, `user_id` (ForeignKey), `token_hash` (String, unique), `expires_at` (DateTime).

### Task 4.2: Email Service
-   **File**: `app/services/email_service.py`
-   **Action**: Create a service for sending emails. For development, this can just log to the console.
-   **Details**:
    -   Implement `send_password_reset_email(email_to: str, reset_link: str)`.

### Task 4.3: Auth Service Logic
-   **File**: `app/services/auth_service.py`
-   **Actions**:
    -   **Request Logic**:
        -   Generate a cryptographically secure random token.
        -   Hash the token before storing it in the `password_reset_tokens` table with an expiration (e.g., 1 hour).
        -   Call the `email_service` with the plain token.
    -   **Confirmation Logic**:
        -   Hash the incoming plain token to find it in the database.
        -   Verify the token hasn't expired.
        -   Update the user's `hashed_password` with the new one.
        -   Delete the reset token so it cannot be used again.

### Task 4.4: Endpoints
-   **File**: `app/api/v1/endpoints/auth.py`
-   **Actions**:
    -   `POST /password-reset/request`: Takes an email, calls the request logic in `auth_service`. Always returns a generic "if a user with that email exists..." message.
    -   `POST /password-reset/confirm`: Takes the token and a new password, calls the confirmation logic in `auth_service`.

---

## Phase 5: Multi-Factor Authentication (MFA)

**Objective**: Add an optional, second layer of security using TOTP.

### Task 5.1: Update User Model
-   **File**: `app/models/user.py`
-   **Action**: Add MFA fields to the `User` model.
-   **Details**:
    -   `mfa_secret`: String, nullable. **This must be encrypted at rest in the database.**
    -   `mfa_enabled`: Boolean, default `False`.

### Task 5.2: Security & Service Logic
-   **Files**: `app/core/security.py`, `app/services/auth_service.py`
-   **Actions**:
    -   **`security.py`**:
        -   Add `pyotp` functions: `generate_mfa_secret()`, `get_totp_uri()`, `verify_mfa_code(secret, code)`.
        -   Add functions to encrypt/decrypt the MFA secret before storing/retrieving it from the DB.
    -   **`auth_service.py`**:
        -   `enable_mfa`: Generates a secret, encrypts it, stores it on the user model (but `mfa_enabled` is still false). Returns the plain secret and a QR code URI to the user.
        -   `verify_mfa`: Takes a TOTP code from the user. If it's valid, it sets `mfa_enabled = True` for that user.
        -   `disable_mfa`: Sets `mfa_enabled = False`.
    -   **Modify `auth_service.authenticate_user`**: If the user has `mfa_enabled`, the standard password check is only the first step. The endpoint must then require a second step for TOTP verification.

### Task 5.3: Endpoints
-   **File**: `app/api/v1/endpoints/auth.py`
-   **Actions**:
    -   `POST /mfa/enable`: Kicks off the process.
    -   `POST /mfa/verify`: Confirms the setup.
    -   `POST /mfa/disable`: Turns off MFA.
    -   Modify the `/token` endpoint:
        -   If `authenticate_user` succeeds but the user has `mfa_enabled`, return a custom response (e.g., `423 Locked` with `error: "mfa_required"`) instead of tokens.
        -   The login form must then make a second call to `/token`, this time including the `mfa_code`.

---

## Phase 6: Testing and Hardening

**Objective**: Ensure the entire authentication system is robust and secure against attacks.

-   **Testing**:
    -   Write comprehensive integration tests for every scenario:
        -   Login success/failure (wrong password, wrong email).
        -   MFA-enabled login success/failure.
        -   Password reset request and confirmation.
        -   Expired/invalid password reset token.
        -   Token refresh success/failure.
        -   Accessing a protected endpoint with/without/with an expired token.
-   **Security Hardening**:
    -   **Rate Limiting**: Apply strict rate limits (`slowapi`) to `/token`, `/password-reset/request`, and `/mfa/verify` to prevent brute-force attacks.
    -   **Logging**: Implement detailed, structured logging for all security-sensitive events (e.g., "Login failed for user X from IP Y", "Password reset requested for user Z").
    -   **Code Review**: Conduct a peer review focused specifically on security vulnerabilities.

By executing this plan, your team will systematically build an enterprise-grade authentication API that is secure, maintainable, and fully-featured. 