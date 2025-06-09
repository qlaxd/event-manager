# API Specifications: UCC Event Manager

## 1. Overview

This document defines the RESTful API specifications for the UCC Event Manager system. The API provides secure endpoints for user authentication, event management, helpdesk functionality, and administrative operations.

### 1.1 Base Information

- **Base URL**: `https://api.ucc-event-manager.com/api/v1`
- **Protocol**: HTTPS only (TLS 1.2+)
- **Authentication**: OAuth2.0 Password Flow with JWT tokens
- **Content Type**: `application/json`
- **API Version**: v1

### 1.2 Security Requirements

- All endpoints require HTTPS
- Authentication required for all protected endpoints
- Rate limiting applied to prevent abuse
- Input validation and sanitization
- CORS configuration for frontend access
- Protection against OWASP Top 10 risks

---

## 2. Authentication & Authorization

### 2.1 OAuth2.0 Token Endpoint

#### POST /auth/token

Authenticate user and issue JWT tokens.

**Request:**

```json
{
  "grant_type": "password",
  "email": "user@example.com",
  "password": "securepassword123",
  "mfa_code": "123456"  // Optional, required if MFA enabled
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "def502008b14e1e6b9b9c7a5c9e5f6a2b1c3d4e5f6...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "read write"
}
```

**Response (401 Unauthorized):**

```json
{
  "error": "invalid_grant",
  "error_description": "Invalid email or password"
}
```

**Response (423 Locked):**

```json
{
  "error": "mfa_required",
  "error_description": "Multi-factor authentication code required"
}
```

### 2.2 Token Refresh

#### POST /auth/refresh

Refresh an expired access token using a refresh token.

**Request:**

```json
{
  "grant_type": "refresh_token",
  "refresh_token": "def502008b14e1e6b9b9c7a5c9e5f6a2b1c3d4e5f6..."
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "def502008b14e1e6b9b9c7a5c9e5f6a2b1c3d4e5f6...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 2.3 Token Revocation

#### POST /auth/revoke

Revoke a refresh token (logout).

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "token": "def502008b14e1e6b9b9c7a5c9e5f6a2b1c3d4e5f6...",
  "token_type_hint": "refresh_token"
}
```

**Response (200 OK):**

```json
{
  "message": "Token revoked successfully"
}
```

### 2.4 Password Reset Request

#### POST /auth/password-reset/request

Request a password reset token.

**Request:**

```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**

```json
{
  "message": "Password reset email sent if account exists"
}
```

### 2.5 Password Reset Confirmation

#### POST /auth/password-reset/confirm

Reset password using the token from email.

**Request:**

```json
{
  "token": "abc123def456ghi789jkl012mno345pqr678stu901",
  "new_password": "newsecurepassword123"
}
```

**Response (200 OK):**

```json
{
  "message": "Password reset successfully"
}
```

**Response (400 Bad Request):**

```json
{
  "error": "invalid_token",
  "error_description": "Token is invalid or expired"
}
```

---

## 3. Multi-Factor Authentication (MFA)

### 3.1 Enable MFA

#### POST /auth/mfa/enable

Enable MFA for the authenticated user.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "password": "currentpassword123"
}
```

**Response (200 OK):**

```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "backup_codes": [
    "12345678",
    "87654321",
    "11223344"
  ]
}
```

### 3.2 Verify MFA Setup

#### POST /auth/mfa/verify

Verify MFA setup with TOTP code.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "mfa_code": "123456"
}
```

**Response (200 OK):**

```json
{
  "message": "MFA enabled successfully"
}
```

### 3.3 Disable MFA

#### POST /auth/mfa/disable

Disable MFA for the authenticated user.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "password": "currentpassword123",
  "mfa_code": "123456"
}
```

**Response (200 OK):**

```json
{
  "message": "MFA disabled successfully"
}
```

---

## 4. User Management

### 4.1 Get Current User Profile

#### GET /users/me

Get the authenticated user's profile information.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "mfa_enabled": true,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 4.2 Update User Profile

#### PATCH /users/me

Update the authenticated user's profile.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "full_name": "John Smith"
}
```

**Response (200 OK):**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "full_name": "John Smith",
  "mfa_enabled": true,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T15:45:00Z"
}
```

### 4.3 Change Password

#### POST /users/me/change-password

Change the authenticated user's password.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

**Response (200 OK):**

```json
{
  "message": "Password changed successfully"
}
```

---

## 5. Event Management

### 5.1 List User Events

#### GET /events

Get a list of events for the authenticated user.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

- `limit` (integer, optional): Number of events to return (default: 50, max: 100)
- `offset` (integer, optional): Number of events to skip (default: 0)
- `sort` (string, optional): Sort field (`occurrence`, `created_at`, `title`) (default: `occurrence`)
- `order` (string, optional): Sort order (`asc`, `desc`) (default: `asc`)
- `from_date` (string, optional): Filter events from date (ISO 8601 format)
- `to_date` (string, optional): Filter events to date (ISO 8601 format)

**Response (200 OK):**

```json
{
  "events": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174001",
      "title": "Team Meeting",
      "occurrence": "2024-02-15T14:30:00Z",
      "description": "Weekly team sync meeting",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "123e4567-e89b-12d3-a456-426614174002",
      "title": "Project Deadline",
      "occurrence": "2024-02-28T23:59:00Z",
      "description": null,
      "created_at": "2024-01-20T09:15:00Z",
      "updated_at": "2024-01-20T09:15:00Z"
    }
  ],
  "total": 25,
  "limit": 50,
  "offset": 0
}
```

### 5.2 Get Single Event

#### GET /events/{event_id}

Get details of a specific event.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174001",
  "title": "Team Meeting",
  "occurrence": "2024-02-15T14:30:00Z",
  "description": "Weekly team sync meeting",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Response (404 Not Found):**

```json
{
  "error": "event_not_found",
  "error_description": "Event not found or access denied"
}
```

### 5.3 Create Event

#### POST /events

Create a new event for the authenticated user.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "title": "Team Meeting",
  "occurrence": "2024-02-15T14:30:00Z",
  "description": "Weekly team sync meeting"
}
```

**Response (201 Created):**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174001",
  "title": "Team Meeting",
  "occurrence": "2024-02-15T14:30:00Z",
  "description": "Weekly team sync meeting",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Response (400 Bad Request):**

```json
{
  "error": "validation_error",
  "error_description": "Invalid input data",
  "details": {
    "title": ["Title is required"],
    "occurrence": ["Invalid date format"]
  }
}
```

### 5.4 Update Event

#### PATCH /events/{event_id}

Update an existing event (only description can be modified).

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "description": "Updated weekly team sync meeting with new agenda"
}
```

**Response (200 OK):**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174001",
  "title": "Team Meeting",
  "occurrence": "2024-02-15T14:30:00Z",
  "description": "Updated weekly team sync meeting with new agenda",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T16:45:00Z"
}
```

### 5.5 Delete Event

#### DELETE /events/{event_id}

Delete an existing event.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

**Response (404 Not Found):**

```json
{
  "error": "event_not_found",
  "error_description": "Event not found or access denied"
}
```

---

## 6. Helpdesk Chatbot

### 6.1 Send Chat Message

#### POST /helpdesk/chat

Send a message to the helpdesk chatbot.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "message": "How do I create a new event?",
  "session_id": "sess_123e4567-e89b-12d3-a456-426614174000"
}
```

**Response (200 OK):**

```json
{
  "response": "To create a new event, click the 'Add Event' button on your dashboard and fill in the required fields: title and occurrence date/time. You can also add an optional description.",
  "session_id": "sess_123e4567-e89b-12d3-a456-426614174000",
  "confidence": 0.95,
  "escalation_suggested": false,
  "quick_replies": [
    "How do I edit an event?",
    "How do I delete an event?",
    "Speak to a human agent"
  ]
}
```

### 6.2 Escalate to Human Agent

#### POST /helpdesk/escalate

Escalate the conversation to a human agent.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "session_id": "sess_123e4567-e89b-12d3-a456-426614174000",
  "reason": "chatbot_unable_to_help",
  "message": "I need help with a specific technical issue"
}
```

**Response (200 OK):**

```json
{
  "ticket_id": "TKT-2024-001234",
  "message": "Your request has been escalated to a human agent. Ticket ID: TKT-2024-001234",
  "estimated_wait_time": "15 minutes"
}
```

### 6.3 Get Chat History

#### GET /helpdesk/sessions/{session_id}/messages

Get chat history for a session.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "session_id": "sess_123e4567-e89b-12d3-a456-426614174000",
  "messages": [
    {
      "id": "msg_001",
      "sender": "user",
      "message": "How do I create a new event?",
      "timestamp": "2024-01-20T10:30:00Z"
    },
    {
      "id": "msg_002",
      "sender": "bot",
      "message": "To create a new event, click the 'Add Event' button...",
      "timestamp": "2024-01-20T10:30:02Z",
      "confidence": 0.95
    }
  ]
}
```

---

## 7. Voice Helpdesk (Bonus Feature)

### 7.1 Start Voice Session

#### POST /helpdesk/voice/session

Start a new voice helpdesk session.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "preferred_language": "en-US"
}
```

**Response (200 OK):**

```json
{
  "session_id": "voice_sess_123e4567-e89b-12d3-a456-426614174000",
  "websocket_url": "wss://api.ucc-event-manager.com/helpdesk/voice/ws",
  "token": "voice_token_abc123",
  "expires_in": 1800
}
```

### 7.2 Process Voice Message

#### POST /helpdesk/voice/process

Process a voice message (from phone or web).

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "session_id": "voice_sess_123e4567-e89b-12d3-a456-426614174000",
  "audio_data": "base64_encoded_audio_data",
  "audio_format": "wav",
  "sample_rate": 16000
}
```

**Response (200 OK):**

```json
{
  "transcription": "How do I create a new event?",
  "response": "To create a new event, click the 'Add Event' button on your dashboard...",
  "audio_response": "base64_encoded_audio_response",
  "session_id": "voice_sess_123e4567-e89b-12d3-a456-426614174000"
}
```

---

## 8. Administrative Endpoints

### 8.1 Health Check

#### GET /health

Check API health status (no authentication required).

**Response (200 OK):**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00Z",
  "version": "1.0.0",
  "environment": "production",
  "database": "connected",
  "chatbot": "available"
}
```

### 8.2 System Information

#### GET /system/info

Get system information (admin access required).

**Headers:**

```
Authorization: Bearer <admin_access_token>
```

**Response (200 OK):**

```json
{
  "version": "1.0.0",
  "build": "2024.01.20.1",
  "environment": "production",
  "database_version": "PostgreSQL 15.4",
  "total_users": 1250,
  "total_events": 8934,
  "uptime": "7 days, 14 hours, 23 minutes"
}
```

---

## 9. Error Responses

### 9.1 Standard Error Format

All error responses follow this format:

```json
{
  "error": "error_code",
  "error_description": "Human-readable error description",
  "details": {
    "field": ["Specific field error messages"]
  },
  "timestamp": "2024-01-20T10:30:00Z",
  "request_id": "req_123e4567-e89b-12d3-a456-426614174000"
}
```

### 9.2 Common Error Codes

| Status Code | Error Code              | Description                               |
| ----------- | ----------------------- | ----------------------------------------- |
| 400         | `bad_request`           | Invalid request format or parameters      |
| 400         | `validation_error`      | Input validation failed                   |
| 401         | `unauthorized`          | Authentication required                   |
| 401         | `invalid_token`         | Invalid or expired token                  |
| 403         | `forbidden`             | Insufficient permissions                  |
| 404         | `not_found`             | Resource not found                        |
| 409         | `conflict`              | Resource conflict (e.g., duplicate email) |
| 422         | `unprocessable_entity`  | Request valid but cannot be processed     |
| 429         | `rate_limit_exceeded`   | Too many requests                         |
| 500         | `internal_server_error` | Server error                              |
| 502         | `bad_gateway`           | External service error                    |
| 503         | `service_unavailable`   | Service temporarily unavailable           |

---

## 10. Rate Limiting

### 10.1 Rate Limit Headers

All responses include rate limiting headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642684800
X-RateLimit-Window: 3600
```

### 10.2 Rate Limits by Endpoint Category

| Category       | Limit         | Window     |
| -------------- | ------------- | ---------- |
| Authentication | 5 requests    | 15 minutes |
| Password Reset | 3 requests    | 60 minutes |
| Events CRUD    | 100 requests  | 60 minutes |
| Helpdesk Chat  | 50 requests   | 60 minutes |
| Voice Helpdesk | 20 requests   | 60 minutes |
| General API    | 1000 requests | 60 minutes |

---

## 11. Security Headers

All API responses include security headers:

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
```

---

## 12. CORS Configuration

### 12.1 Allowed Origins

- `https://app.ucc-event-manager.com` (production frontend)
- `https://staging.ucc-event-manager.com` (staging frontend)
- `http://localhost:3000` (development only)

### 12.2 Allowed Methods

- `GET`, `POST`, `PATCH`, `DELETE`, `OPTIONS`

### 12.3 Allowed Headers

- `Authorization`, `Content-Type`, `X-Requested-With`

---

## 13. Data Validation Rules

### 13.1 User Data

- **Email**: Valid email format, max 255 characters, case-insensitive
- **Password**: 8-128 characters, must contain uppercase, lowercase, number
- **Full Name**: 1-255 characters, no HTML tags
- **MFA Code**: 6 digits

### 13.2 Event Data

- **Title**: 1-255 characters, required, no HTML tags
- **Occurrence**: Valid ISO 8601 datetime, required
- **Description**: 0-10,000 characters, optional, basic HTML sanitization

### 13.3 Helpdesk Data

- **Message**: 1-1,000 characters, required
- **Session ID**: Valid UUID format

---

## 14. Pagination

### 14.1 Request Parameters

- `limit`: Number of items to return (default: 50, max: 100)
- `offset`: Number of items to skip (default: 0)

### 14.2 Response Format

```json
{
  "data": [...],
  "total": 150,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

---

## 15. Webhooks (Future Enhancement)

### 15.1 Event Notifications

Webhook endpoints for real-time notifications:

- `event.created`
- `event.updated`
- `event.deleted`
- `user.login`
- `helpdesk.escalated`

### 15.2 Webhook Format

```json
{
  "event": "event.created",
  "data": {
    "event_id": "123e4567-e89b-12d3-a456-426614174001",
    "user_id": "123e4567-e89b-12d3-a456-426614174000"
  },
  "timestamp": "2024-01-20T10:30:00Z"
}
```

---

*This API specification is version 1.0 and is subject to change. For the latest updates, see the API documentation portal.*