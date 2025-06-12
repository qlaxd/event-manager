# Password Reset Feature: Security Analysis & Frontend Implementation Plan

This document provides a security analysis of the current password reset flow and a detailed plan for implementing the frontend components for resetting a user's password.

## 1. Security Analysis of Password Reset Request Flow

This section analyzes the security of the link generation and the existing "Forgot Password" feature.

### 1.1. Backend Implementation (Token Generation)

The backend implementation for generating password reset tokens is generally strong and follows security best practices.

-   **[PASS] Token Generation**: Uses `secrets.token_urlsafe(32)` to create a 256-bit cryptographically secure token. This is excellent.
-   **[PASS] Token Storage**: Hashes the token before storing it in the database. This prevents account takeover if the database is compromised.
-   **[PASS] Rate Limiting**: The `/password-reset/request` endpoint is rate-limited (`10/minute`), which helps prevent email flooding and abuse.
-   **[PASS] User Enumeration Prevention**: The backend is designed to always return a `200 OK` response to prevent attackers from discovering valid user emails.

### 1.2. Identified Vulnerabilities and Areas for Improvement

-   **[CRITICAL] Insecure Reset Link Transmission (HTTP)**
    -   **Issue**: The reset link is generated using `http://localhost:5173`. In a production environment, sending a security token over an unencrypted `HTTP` connection is a critical vulnerability. An attacker on the same network can intercept the token (Man-in-the-Middle attack) and take over the user's account.
    -   **Recommendation**: The `FRONTEND_URL` in the backend configuration **MUST** use `HTTPS` in staging and production environments. All traffic must be forced to HTTPS.

-   **[LOW] Malformed URL (Double Slash)**
    -   **Issue**: The generated URL contains a double slash (`//reset-password`). While most browsers handle this gracefully, it indicates a small bug in URL construction.
    -   **Recommendation**: In the backend's `.env` or settings file, ensure the `FRONTEND_URL` does not have a trailing slash (e.g., `FRONTEND_URL=https://myapp.com` instead of `FRONTEND_URL=https://myapp.com/`).

-   **[HIGH] Frontend User Enumeration Vulnerability**
    -   **Issue**: The `ForgotPasswordView.vue` component contains logic to handle a `404 Not Found` error by displaying "No account found with this email address." This completely undermines the backend's user enumeration protection. An attacker can use this to check for the existence of user accounts.
    -   **Recommendation**: The frontend logic must be changed. It should **never** indicate whether an email address exists in the system. After a user submits their email, the UI should only display a generic, consistent message like: "If an account with that email exists, a password reset link has been sent."

## 2. Frontend Implementation Plan: Reset Password Page

This section details the tasks for creating the new page where users can set a new password after clicking the reset link.

### 2.1. Project Setup

-   [ ] **Create New File**: Create a new Vue component at `frontend/src/views/ResetPasswordView.vue`.
-   [ ] **Setup Routing**:
    -   [ ] In `frontend/src/router/index.ts`, add a new route:
        ```javascript
        {
          path: '/reset-password',
          name: 'reset-password',
          component: () => import('../views/ResetPasswordView.vue'),
          meta: {
            requiresAuth: false // This page must be accessible to unauthenticated users
          }
        }
        ```
    -   The component will access the `token` from the URL query string (`?token=...`).

### 2.2. Component Development (`ResetPasswordView.vue`)

#### 2.2.1. Template (HTML)

-   [ ] Create a form for password reset.
-   [ ] Add an `<h1>` or `<h2>` title: "Set a New Password".
-   [ ] Add an input field for "New Password" (`<input type="password">`).
-   [ ] Add an input field for "Confirm New Password" (`<input type="password">`).
-   [ ] Include a password strength indicator component. This component should display the requirements from `frontend/src/utils/validation.ts` (e.g., min 8 characters, uppercase, lowercase, number).
-   [ ] Add a "Set New Password" submit button. The button should be disabled while the form submission is in progress.
-   [ ] Add a designated area to display error messages (e.g., "Invalid or expired link", "Passwords do not match").
-   [ ] Add a designated area to display a success message upon completion, including a link to the login page.

#### 2.2.2. Script (TypeScript Logic)

-   [ ] **Import Dependencies**: Import `ref`, `onMounted` from `vue`, `useRoute`, `useRouter` from `vue-router`, and the new `resetPassword` function from `AuthService`.
-   [ ] **Component State**:
    -   [ ] `token = ref<string | null>(null)`
    -   [ ] `newPassword = ref('')`
    -   [ ] `confirmPassword = ref('')`
    -   [ ] `loading = ref(false)`
    -   [ ] `errorMessage = ref('')`
    -   [ ] `successMessage = ref('')`
-   [ ] **Token Extraction**:
    -   [ ] Use the `onMounted` lifecycle hook to get the route using `useRoute()`.
    -   [ ] Extract the `token` from `route.query.token`.
    -   [ ] **Security**: If the token is not present, redirect the user to the login page or display an "Invalid Link" error message.
-   [ ] **Form Submission Logic (`handleSubmit`)**:
    -   [ ] Prevent default form submission.
    -   [ ] Clear previous error/success messages.
    -   [ ] **Client-Side Validation**:
        -   [ ] Check that `newPassword` and `confirmPassword` are not empty.
        -   [ ] Check that `newPassword` matches `confirmPassword`.
        -   [ ] Use `validatePassword` from `frontend/src/utils/validation.ts` to enforce password complexity rules.
    -   [ ] If validation fails, display appropriate error messages.
    -   [ ] If validation passes:
        -   [ ] Set `loading.value = true`.
        -   [ ] Call the `resetPassword` service function: `await authService.resetPassword(token.value, newPassword.value)`.
-   [ ] **Success Handling**:
    -   [ ] On successful API response, set `loading.value = false`.
    -   [ ] Clear the password fields for security.
    -   [ ] Display a clear success message: "Your password has been reset successfully. You can now log in."
    -   [ ] Provide a button or `RouterLink` to the `/login` page.
-   [ ] **Error Handling**:
    -   [ ] In a `catch` block, set `loading.value = false`.
    -   [ ] Based on the error status code from the backend:
        -   `400` (Validation Error), `404` (Not Found), `422` (Invalid Token): Display a generic and non-revealing error message like "This password reset link is invalid or has expired. Please try again."
        -   `429` (Too Many Requests): "You have made too many attempts. Please try again later."
        -   `500` (Server Error): "An unexpected error occurred. Please try again."
    -   [ ] **Security**: Do not leak specific details about why the token failed (e.g., "token expired" vs. "token not found").

### 2.3. Service Layer (`frontend/src/services/auth.ts`)

-   [ ] **Add New `resetPassword` Method**:
    -   [ ] Define a new async function `resetPassword(token: string, new_password: string)`.
    -   [ ] It should make a `POST` request to a new backend endpoint, e.g., `/auth/password-reset/confirm`.
    -   [ ] The request body should be an object: `{ token, new_password }`.
    -   [ ] The method should return the response from the server or handle errors.

## 3. Required Backend Changes

For this feature to work, a corresponding backend endpoint must be created.

-   [ ] **Create New Endpoint**: `POST /api/v1/auth/password-reset/confirm`
-   [ ] **Rate Limit**: Apply a strict rate limit to this endpoint (e.g., `5/minute`) to prevent brute-force attacks on tokens.
-   [ ] **Logic**:
    1.  Accept `token` and `new_password` in the request body.
    2.  Validate `new_password` against complexity rules.
    3.  Hash the incoming `token` using the same method as during creation.
    4.  Search for the hashed token in the `password_reset_tokens` database table.
    5.  **Security Checks**:
        -   If the token is not found, return `422 Unprocessable Entity`.
        -   If the token is found but has expired, return `422`.
        -   If the token is found but has already been used, return `422`.
    6.  If all checks pass:
        -   Retrieve the `user_id` associated with the token.
        -   Update the user's password with the new, securely hashed password.
        -   **Invalidate the token** by deleting it or marking it as used to prevent reuse.
        -   Log the successful password reset as a security event.
        -   Return a `200 OK` success response. 