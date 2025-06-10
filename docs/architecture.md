# Architecture: UCC Event Manager

## 1. Overview

The UCC Event Manager is a secure, multi-user event management platform with a clear separation between frontend and backend, communicating exclusively via a RESTful API over HTTPS. The system is designed for security, scalability, and maintainability, and includes advanced features such as a helpdesk chatbot and optional voice-based support.

---

## 2. High-Level System Diagram

```
+-------------------+        HTTPS        +-------------------+        SQL/TCP        +-------------------+
|    Frontend SPA   | <----------------> |     Backend API   | <------------------> |    PostgreSQL DB  |
|   (Vue 3 + Vite)  |                    |   (FastAPI/Python)|                     | (Encrypted at rest)|
+-------------------+                    +-------------------+                     +-------------------+
         |                                        |
         |                                        | HTTP
         |                                        v
         |                              +-------------------+
         |                              |   Rasa Chatbot    |
         |                              +-------------------+
         |                                        |
         |                                        | Webhook
         |                                        v
         |                              +-------------------+
         |                              |  Twilio/Web Voice |
         |                              +-------------------+
```

---

## 3. Component Breakdown

### 3.1 Frontend (Vue 3 SPA)

- **Framework:** Vue 3 (Composition API), Vite, Pinia (state), Vue Router
- **Responsibilities:**
  - User authentication (login, MFA, password reset)
  - Event CRUD UI (list, create, edit, delete)
  - Helpdesk chat widget
  - Voice helpdesk integration (Web Speech API, bonus)
  - Secure token storage (memory or HttpOnly cookie)
  - Responsive, accessible UI

### 3.2 Backend API (FastAPI)

- **Framework:** FastAPI (Python 3.11+), Uvicorn
- **Responsibilities:**
  - RESTful API for all business logic
  - OAuth2.0 password flow, JWT access/refresh tokens
  - MFA (TOTP) support
  - Password reset (token-based)
  - Event CRUD endpoints (per-user)
  - User management (seed/admin only)
  - Integration with Rasa chatbot (HTTP)
  - Integration with Twilio/Web Voice (webhook)
  - Security: input validation, rate limiting, CORS, HTTPS enforcement
  - Logging and monitoring

### 3.3 Database (PostgreSQL)

- **Responsibilities:**
  - Store users, events, password reset tokens, MFA secrets
  - Encrypted at rest (TDE or field-level encryption)
  - Secure password hashing (bcrypt/argon2)
  - Row-level security (optional)

### 3.4 Rasa Chatbot (Dockerized Service)

- **Responsibilities:**
  - NLP for helpdesk Q&A
  - Intent recognition, FAQ, escalation detection
  - HTTP API for backend integration
  - Training data and stories managed in repo

### 3.5 Voice Integration (Bonus)

- **Twilio Programmable Voice** or **Web Speech API**
- **Responsibilities:**
  - Accept voice queries (phone or browser)
  - Transcribe to text (STT)
  - Forward to backend for chatbot processing
  - Respond with TTS or escalate to human

### 3.6 Nginx (Reverse Proxy, TLS)

- **Responsibilities:**
  - TLS termination (HTTPS enforcement)
  - Proxy requests to backend and frontend
  - CORS and security headers
  - (Optional) Serve static frontend build

---

## 4. Data Flow

### 4.1 Authentication

1. User submits login form (email, password) to backend API.
2. Backend validates credentials, issues JWT access/refresh tokens.
3. If MFA enabled, backend requests TOTP code before issuing tokens.
4. Frontend stores token securely (memory or HttpOnly cookie).

### 4.2 Event CRUD

1. Authenticated frontend requests event data (GET /events) with JWT.
2. Backend validates JWT, queries DB for user's events, returns data.
3. Create/update/delete operations follow similar flow, always per-user.

### 4.3 Password Reset

1. User requests password reset (POST /auth/forgot-password).
2. Backend generates time-limited token, sends email (or logs link in dev).
3. User submits new password with token (POST /auth/reset-password).
4. Backend validates token, updates password hash in DB.

### 4.4 Helpdesk Chatbot

1. User submits question via chat widget (POST /helpdesk/query).
2. Backend forwards question to Rasa (HTTP API).
3. Rasa returns answer, confidence, and escalation flag.
4. Backend relays response to frontend; frontend offers escalation if needed.

### 4.5 Voice Helpdesk (Bonus)

1. User initiates voice session (phone or browser).
2. Voice input is transcribed (STT) and sent to backend (/helpdesk/voice).
3. Backend processes as chatbot query, returns TTS response.
4. If escalation needed, call is routed to human agent (Twilio <Dial> or similar).

---

## 5. Security Architecture

- **HTTPS enforced everywhere (Nginx reverse proxy, self-signed certs in dev)**
- **OAuth2.0 + JWT for all API access**
- **MFA (TOTP) for users who enable it**
- **Password reset tokens: single-use, time-limited, stored hashed**
- **Passwords: hashed with bcrypt/argon2, salted**
- **Database encryption at rest (TDE or field-level)**
- **Input validation (Pydantic schemas)**
- **Rate limiting and brute-force protection**
- **CORS: only allow frontend origin**
- **No sensitive data in logs**
- **OWASP Top 10 mitigations (see security.md)**

---

## 6. Integration Points

- **Frontend ↔ Backend:** REST API over HTTPS
- **Backend ↔ Database:** SQLAlchemy ORM (Python) over secure TCP
- **Backend ↔ Rasa:** HTTP API (Docker network or secure internal endpoint)
- **Backend ↔ Twilio/Web Voice:** Webhook endpoints for voice events
- **Nginx ↔ All services:** Reverse proxy, TLS, security headers

---

## 7. Deployment & DevOps

- **Docker Compose** for local development (services: frontend, backend, db, rasa, nginx)
- **CI/CD:** GitHub Actions for linting, testing, building images
- **Environments:**
  - Development: self-signed TLS, local SMTP/log for emails
  - Staging/Production: real TLS certs, SMTP, monitoring
- **Monitoring:**
  - Backend: logging, error tracking
  - DB: connection and query monitoring
  - Uptime checks for all services

---

## 8. Scalability & Maintainability

- **Stateless backend:** easy to scale horizontally
- **Frontend SPA:** can be served via CDN or static hosting
- **Database:** vertical scaling, backups, encryption
- **Chatbot/Voice:** can be containerized and scaled independently
- **Clear separation of concerns:** modular codebase, documented APIs

---

## 9. Diagrams (to be added)

- [ ] High-level architecture (see above ASCII)
- [ ] Data model/ERD (see data-model.md)
- [ ] API flow diagrams (login, event CRUD, helpdesk)
- [ ] Sequence diagrams for key flows (optional)

---

## 10. Future Considerations

- **Admin UI for user management**
- **Kubernetes deployment for production**
- **Advanced monitoring and alerting**
- **Additional chatbot intents and training**
- **Internationalization (i18n) support**

---

*For detailed API specs, see [api-spec.md]. For security details, see [security.md]. For user journeys, see [user-stories.md].* 