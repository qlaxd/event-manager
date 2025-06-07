# Backend API File Structure: UCC Event Manager

## 1. Overview
This document outlines the complete file and directory structure for the FastAPI backend of the UCC Event Manager. The structure is designed to be modular, scalable, and maintainable, following best practices for modern Python web applications. It clearly separates concerns such as API routing, business logic, data access, and core functionalities like security and configuration.

---

## 2. Root Directory
The root directory contains configuration files, containerization setup, and the main application directory.

```
/backend
├── .env.example              # Example environment variables for local development
├── .gitignore                # Specifies files and directories to be ignored by Git
├── alembic.ini               # Configuration file for Alembic database migrations
├── docker-compose.yml        # Docker Compose file to orchestrate services (backend, db, etc.)
├── Dockerfile                # Dockerfile for building the backend service container
├── pyproject.toml            # Poetry project file for dependency management and project metadata
├── README.md                 # Project overview, setup, and usage instructions
|
├── alembic/                  # Directory for Alembic database migration scripts
│   ├── env.py                # Alembic script to configure and run migrations
│   ├── script.py.mako        # Template for new migration scripts
│   └── versions/             # Contains individual, versioned migration files
|
├── app/                      # Main application source code directory
│   └── ...
|
├── keys/                     # Directory for storing cryptographic keys (MUST be in .gitignore)
│   ├── jwt-private.pem       # Private RSA key for signing JWTs
│   └── jwt-public.pem        # Public RSA key for verifying JWTs
|
├── scripts/                  # Utility and operational scripts
│   ├── seed_db.py            # Script to seed the database with initial data (e.g., admin user)
│   └── run_dev.sh            # Development server startup script
|
└── tests/                    # Application test suite
    └── ...
```

---

## 3. Application Directory (`app/`)
This is where the core logic of the application resides.

```
/app
├── __init__.py               # Initializes the 'app' package
├── main.py                   # Main FastAPI application entry point
|
├── api/                      # API-specific modules, including routing and versioning
│   ├── __init__.py           # Initializes the 'api' package
│   └── v1/                   # API version 1
│       ├── __init__.py       # Initializes the 'v1' package
│       ├── api_router.py     # Main router for API v1, includes all endpoint routers
│       └── endpoints/        # Directory containing individual API endpoint routers
│           ├── __init__.py
│           ├── auth.py         # Authentication routes (/token, /password-reset, etc.)
│           ├── events.py       # Event CRUD routes (/events)
│           ├── helpdesk.py     # Helpdesk routes (/helpdesk/chat, /helpdesk/voice)
│           └── users.py        # User management routes (/users/me)
|
├── core/                     # Core application components (config, security, etc.)
│   ├── __init__.py
│   ├── config.py             # Pydantic-based application settings management (from .env)
│   ├── database.py           # Database connection and session management (SQLAlchemy)
│   └── security.py           # Security-related logic (password hashing, JWTs, MFA/TOTP)
|
├── models/                   # SQLAlchemy ORM models, defining database tables
│   ├── __init__.py
│   ├── base.py               # Base model class that all models inherit from
│   ├── event.py              # Event model (events table)
│   ├── token.py              # Models for refresh tokens and password reset tokens
│   └── user.py               # User model (users table)
|
├── repositories/             # Data Access Layer (DAL), abstracts database interactions
│   ├── __init__.py
│   ├── base_repository.py    # Base repository with common CRUD methods
│   ├── event_repository.py   # Handles database operations for the Event model
│   └── user_repository.py    # Handles database operations for the User model
|
├── schemas/                  # Pydantic schemas for data validation and serialization
│   ├── __init__.py
│   ├── event.py              # Schemas for event creation, updates, and responses
│   ├── msg.py                # Generic message schema for simple API responses
│   ├── token.py              # Schemas for JWTs and token-related requests/responses
│   └── user.py               # Schemas for user creation, updates, and profiles
|
├── services/                 # Business logic layer, orchestrates operations
│   ├── __init__.py
│   ├── auth_service.py       # Handles authentication logic, token management, MFA
│   ├── email_service.py      # Service for sending emails (e.g., password reset)
│   ├── event_service.py      # Implements business logic for event management
│   ├── helpdesk_service.py   # Integrates with Rasa/voice services
│   └── user_service.py       # Implements business logic for user management
|
└── utils/                    # Shared utility functions and modules
    ├── __init__.py
    └── dependencies.py       # FastAPI dependency injection functions (e.g., get_current_user)
```

---

## 4. Testing Directory (`tests/`)
Contains all tests for the application, mirroring the `app` directory structure.

```
/tests
├── __init__.py
├── conftest.py               # Pytest fixtures and test setup (e.g., test client, db session)
|
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       ├── test_auth_endpoints.py
│       ├── test_event_endpoints.py
│       └── test_user_endpoints.py
|
├── services/
│   ├── __init__.py
│   ├── test_auth_service.py
│   └── test_event_service.py
|
├── repositories/
│   ├── __init__.py
│   ├── test_event_repository.py
│   └── test_user_repository.py
|
└── utils/
    ├── __init__.py
    └── test_security.py      # Tests for security utility functions
``` 