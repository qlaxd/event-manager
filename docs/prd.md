# PRD: UCC Event Manager

## 1. Product overview

### 1.1 Document title and version

- PRD: UCC Event Manager
- Version: 1.0.0

### 1.2 Product summary

The UCC Event Manager is a secure, multi-user event management system designed to allow users to create, view, update, and delete their personal events. The system is architected with a clear separation between the backend (RESTful API) and frontend (SPA), communicating exclusively over secure HTTP. 

The application emphasizes modern security standards, including OAuth2.0 authentication, JWT-based session management, and optional multi-factor authentication (MFA). It also features a helpdesk chatbot capable of understanding free-form user queries, with escalation to a human operator if needed. Voice-based helpdesk access is available as a bonus feature. 

The system is intended to demonstrate best practices in secure software design, user experience, and maintainability, while providing a robust platform for event management and support.

## 2. Goals

### 2.1 Business goals

- Demonstrate technical and security best practices for a modern web application.
- Provide a seamless and secure event management experience for users.
- Showcase advanced features such as chatbot and voice-based helpdesk integration.
- Ensure compliance with industry standards (e.g., OWASP Top 10).

### 2.2 User goals

- Easily manage personal events (create, view, update, delete).
- Access the system securely with modern authentication methods.
- Receive timely support via chatbot or voice helpdesk.
- Reset forgotten passwords securely.

### 2.3 Non-goals

- User self-registration from the frontend.
- Public event sharing or discovery.
- Hardcoded users in the source code.
- Support for legacy browsers or insecure HTTP connections.

## 3. User personas

### 3.1 Key user types

- End users
- Administrators
- Helpdesk agents

### 3.2 Basic persona details

- **End users**: Individuals who need to manage their own events securely and efficiently.
- **Administrators**: Staff responsible for user management, system monitoring, and support escalation.
- **Helpdesk agents**: Personnel who handle escalated support requests from users.

### 3.3 Role-based access

- **End users**: Can log in, manage their own events, interact with the helpdesk, and reset passwords.
- **Administrators**: Can access system logs, manage users, and handle escalated helpdesk requests.
- **Helpdesk agents**: Can respond to escalated support queries and assist users as needed.

## 4. Functional requirements

- **User authentication and session management** (Priority: High)
  - Secure login with email and password.
  - Optional multi-factor authentication (MFA) using TOTP.
  - Password reset via email with time-limited, single-use tokens.
  - OAuth2.0 password flow with JWT access and refresh tokens.
  - No user registration from the frontend; users are seeded or managed via admin tools.
- **Event CRUD operations** (Priority: High)
  - Users can create events with a title (required), occurrence (required), and description (optional).
  - Users can view a list of their own events.
  - Users can update the description of their events.
  - Users can delete their own events.
  - All event operations are protected and require authentication.
- **Helpdesk chatbot** (Priority: Medium)
  - Users can ask free-form questions and receive automated answers.
  - Chatbot can escalate to a human agent if confidence is low or upon user request.
  - Chatbot is accessible from the frontend dashboard.
- **Voice-based helpdesk** (Priority: Low/BONUS)
  - Users can interact with the helpdesk via phone or web voice interface.
  - Voice queries are transcribed and processed by the chatbot.
  - Escalation to a human agent is supported.
- **Security and compliance** (Priority: High)
  - All API endpoints require HTTPS (TLS enforced).
  - Data is stored securely with encryption at rest (e.g., PostgreSQL TDE, hashed passwords).
  - Protection against OWASP Top 10 risks (input validation, rate limiting, CORS, etc.).
  - JWT refresh tokens are revocable.
- **Admin and support tools** (Priority: Medium)
  - Admins can view logs and manage users (out of scope for MVP, but planned).

## 5. User experience

### 5.1. Entry points & first-time user flow

- Login page with email and password fields.
- "Forgot password?" link for password reset.
- Dashboard as the main entry after login.
- Helpdesk chat widget accessible from the dashboard.

### 5.2. Core experience

- **Login:** User enters email and password to access the dashboard.
  - Clear error messages for invalid credentials or MFA requirements.
- **Dashboard:** User sees a table of their events.
  - Events are listed with title, occurrence, and description.
- **Create event:** User clicks "Add Event" and fills in required fields.
  - Form validation ensures title and occurrence are provided.
- **Edit event:** User can update the description of an event via an edit modal.
  - Only the description is editable after creation.
- **Delete event:** User can delete an event with confirmation.
  - Immediate feedback on success or failure.
- **Helpdesk chat:** User can ask questions in a chat widget.
  - Automated answers are provided; escalation option appears if needed.

### 5.3. Advanced features & edge cases

- MFA setup and verification for users who enable it.
- Password reset flow with email token validation.
- Handling expired or invalid JWTs (automatic logout, error message).
- Handling expired or invalid password reset tokens.
- Chatbot fallback to human agent if unable to answer.
- Voice-based helpdesk for users preferring phone/web voice.

### 5.4. UI/UX highlights

- Clean, modern interface using Vue 3 and a component library (e.g., Vuetify or Tailwind).
- Responsive design for desktop and mobile.
- Accessible forms with clear validation and error states.
- Persistent session with secure token storage.
- Intuitive chat widget for helpdesk access.

## 6. Narrative

Anna is a busy professional who needs to keep track of her meetings and deadlines. She logs into the event manager, quickly adds new events, and updates details as needed. When she has a question about using the system, she opens the helpdesk chat and receives instant answers. If her question is too complex, she can escalate to a human agent or even use the voice helpdesk for real-time support. The secure, user-friendly experience gives her confidence that her data is safe and her needs are met efficiently.

## 7. Success metrics

### 7.1. User-centric metrics

- Number of active users managing events.
- User satisfaction with event management and helpdesk features.
- Password reset success rate.
- Average response time for helpdesk queries.

### 7.2. Business metrics

- Successful completion of the evaluation and interview process.
- Positive feedback from evaluators on security and usability.
- Demonstrated compliance with requirements and bonus features.

### 7.3. Technical metrics

- API response times under 300ms for 95% of requests.
- 100% of API traffic over HTTPS.
- Zero critical security vulnerabilities (OWASP Top 10).
- Automated test coverage above 80% for backend and frontend.

## 8. Technical considerations

### 8.1. Integration points

- Frontend (Vue 3 SPA) communicates with backend REST API.
- Backend integrates with PostgreSQL for data storage.
- Backend connects to Rasa (or similar) for chatbot functionality.
- Voice helpdesk integrates with Twilio or Web Speech API.
- Admin tools for user management (planned).

### 8.2. Data storage & privacy

- User and event data stored in PostgreSQL with encryption at rest.
- Passwords hashed with bcrypt or argon2.
- Password reset tokens stored securely with expiration.
- Minimal JWT payload (user_id, exp, iat).
- No sensitive data in logs or error messages.

### 8.3. Scalability & performance

- Docker Compose setup for local development and deployment.
- Stateless backend for easy scaling.
- Caching for frequently accessed data (planned).
- Asynchronous processing for chatbot and voice features.

### 8.4. Potential challenges

- Ensuring robust security for authentication and data storage.
- Handling edge cases in password reset and MFA flows.
- Integrating and training the chatbot for relevant queries.
- Managing voice-based helpdesk integration and reliability.
- Maintaining a clean and intuitive user experience.

## 9. Milestones & sequencing

### 9.1. Project estimate

- Medium: 2-4 weeks

### 9.2. Team size & composition

- Medium Team: 1-3 total people
  - Product manager, 1-2 engineers, 1 designer, 1 QA specialist

### 9.3. Suggested phases

- **Phase 1:** Core authentication, event CRUD, and password reset (1 week)
  - Key deliverables: User login, JWT auth, event management endpoints, password reset flow, basic frontend.
- **Phase 2:** Helpdesk chatbot integration and UI/UX improvements (1 week)
  - Key deliverables: Chatbot backend integration, chat widget, improved dashboard, accessibility enhancements.
- **Phase 3:** Security hardening, admin tools, and bonus features (1-2 weeks)
  - Key deliverables: MFA, voice helpdesk, admin tools, security review, documentation, test coverage.

## 10. User stories

### 10.1. Log in to the system

- **ID**: US-001
- **Description**: As a user, I want to log in with my email and password so that I can access my events securely.
- **Acceptance criteria**:
  - User can enter email and password on the login page.
  - Invalid credentials result in a clear error message.
  - Successful login issues a JWT and redirects to the dashboard.
  - If MFA is enabled, user is prompted for a TOTP code.

### 10.2. Reset forgotten password

- **ID**: US-002
- **Description**: As a user, I want to request a password reset if I forget my password so that I can regain access to my account.
- **Acceptance criteria**:
  - "Forgot password?" link is available on the login page.
  - User can enter their email to request a reset.
  - System sends a reset link with a time-limited token.
  - User can set a new password using the link.
  - Expired or invalid tokens result in an error message.

### 10.3. Set up and use MFA

- **ID**: US-003
- **Description**: As a user, I want to enable multi-factor authentication for my account so that I have an extra layer of security.
- **Acceptance criteria**:
  - User can enable MFA from their account settings.
  - System generates a TOTP secret and displays a QR code.
  - User can verify setup by entering a TOTP code.
  - On subsequent logins, user is prompted for a TOTP code if MFA is enabled.
  - User can disable MFA after verifying their password.

### 10.4. Create a new event

- **ID**: US-004
- **Description**: As a user, I want to create a new event with a title, date/time, and optional description so that I can keep track of important activities.
- **Acceptance criteria**:
  - User can open a form to add a new event.
  - Title and occurrence fields are required; description is optional.
  - Form validation prevents submission without required fields.
  - Event is saved and appears in the event list.

### 10.5. View my events

- **ID**: US-005
- **Description**: As a user, I want to view a list of my events so that I can see upcoming and past activities.
- **Acceptance criteria**:
  - Dashboard displays a table of the user's events.
  - Events are sorted by occurrence date.
  - Each event shows title, occurrence, and description.

### 10.6. Update event description

- **ID**: US-006
- **Description**: As a user, I want to update the description of an existing event so that I can add or change details.
- **Acceptance criteria**:
  - User can open an edit modal for an event.
  - Only the description field is editable.
  - Changes are saved and reflected in the event list.

### 10.7. Delete an event

- **ID**: US-007
- **Description**: As a user, I want to delete an event so that I can remove activities that are no longer relevant.
- **Acceptance criteria**:
  - User can delete an event from the dashboard.
  - Confirmation is required before deletion.
  - Deleted event is removed from the list.

### 10.8. Use the helpdesk chatbot

- **ID**: US-008
- **Description**: As a user, I want to ask questions in a helpdesk chat so that I can get instant support.
- **Acceptance criteria**:
  - Chat widget is accessible from the dashboard.
  - User can type free-form questions.
  - Chatbot provides relevant answers or suggests escalation if needed.
  - User can request escalation to a human agent.

### 10.9. Use the voice-based helpdesk (bonus)

- **ID**: US-009
- **Description**: As a user, I want to interact with the helpdesk using my voice so that I can get support hands-free.
- **Acceptance criteria**:
  - User can initiate a voice session via phone or web.
  - System transcribes and responds to voice queries.
  - Escalation to a human agent is available if needed.

### 10.10. Secure access to all features

- **ID**: US-010
- **Description**: As a user, I want all my data and actions to be protected from unauthorized access so that my information remains private and secure.
- **Acceptance criteria**:
  - All API endpoints require valid authentication.
  - JWT tokens are validated on every request.
  - HTTPS is enforced for all communications.
  - Unauthorized access attempts are logged and denied. 