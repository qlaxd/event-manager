# UCC Event Manager - Backend API

## Overview

The UCC Event Manager backend is a secure, scalable RESTful API built with FastAPI and Python 3.11+. It provides authentication, event management, and helpdesk functionality with enterprise-grade security features.

## Technology Stack

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15.4+ with SQLAlchemy 2.0
- **Authentication**: OAuth2.0 with JWT (RS256)
- **Security**: bcrypt, MFA with TOTP, rate limiting
- **API Documentation**: OpenAPI/Swagger
- **Container**: Docker & Docker Compose

## Features

- ✅ OAuth2.0 authentication with JWT tokens
- ✅ Multi-factor authentication (MFA) with TOTP
- ✅ Password reset via email
- ✅ User event management (CRUD)
- ✅ Helpdesk chatbot integration
- ✅ Voice helpdesk support (bonus feature)
- ✅ Comprehensive security (OWASP Top 10 protection)
- ✅ Rate limiting and brute force protection
- ✅ Structured logging and monitoring
- ✅ Health check endpoints

## Project Structure

```
backend/
├── app/
│   ├── api/           # API route handlers
│   │   └── v1/        # API version 1
│   ├── core/          # Core functionality (config, security, database)
│   ├── models/        # SQLAlchemy database models
│   ├── schemas/       # Pydantic validation schemas
│   ├── services/      # Business logic layer
│   ├── repositories/  # Data access layer
│   └── utils/         # Utility functions
├── alembic/           # Database migrations
├── tests/             # Test suite
├── scripts/           # Utility scripts
├── keys/              # JWT keys (not in git)
├── docker-compose.yml # Docker services configuration
├── Dockerfile         # Container configuration
├── pyproject.toml     # Poetry dependencies
└── alembic.ini        # Alembic configuration
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Poetry (for dependency management)

### Using Docker Compose (Recommended)

1. Clone the repository and navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Copy the example environment file:
   ```bash
   cp example.env .env
   ```

3. Update the `.env` file with your configuration

4. Generate JWT keys:
   ```bash
   mkdir keys
   openssl genrsa -out keys/jwt_private.pem 4096
   openssl rsa -in keys/jwt_private.pem -pubout -out keys/jwt_public.pem
   ```

5. Start the services:
   ```bash
   docker-compose up -d
   ```

6. Run database migrations:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

7. Access the API at `http://localhost:8000`
   - API docs: `http://localhost:8000/api/v1/docs`
   - Health check: `http://localhost:8000/health`

### Local Development Setup

1. Install Poetry:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry env activate
   ```
   
   #### or

   ```bash
   poetry shell
   ```

4. Set up PostgreSQL database (or use Docker):
   ```bash
   docker run -d \
     --name postgres \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=password \
     -e POSTGRES_DB=ucc_events \
     -p 5432:5432 \
     postgres:15.4-alpine
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the development server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Configuration

### Environment Variables

See `example.env` for all available configuration options. Key variables:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Application secret key
- `JWT_PRIVATE_KEY_PATH`: Path to JWT private key
- `JWT_PUBLIC_KEY_PATH`: Path to JWT public key
- `SMTP_*`: Email configuration for password reset
- `RASA_URL`: Rasa chatbot URL (optional)
- `TWILIO_*`: Twilio configuration for voice helpdesk (optional)

### Security Configuration

- Password requirements: 8+ characters, uppercase, lowercase, numbers
- MFA: TOTP-based with 8 backup codes
- Rate limiting: 5 auth attempts/15min, 1000 requests/hour
- Token expiry: Access tokens 1 hour, refresh tokens 30 days

## API Documentation

### Authentication Endpoints

- `POST /api/v1/auth/token` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/revoke` - Logout/revoke token
- `POST /api/v1/auth/password-reset/request` - Request password reset
- `POST /api/v1/auth/password-reset/confirm` - Confirm password reset

### User Management

- `GET /api/v1/users/me` - Get current user profile
- `PATCH /api/v1/users/me` - Update user profile
- `POST /api/v1/users/me/change-password` - Change password

### Event Management

- `GET /api/v1/events` - List user events
- `POST /api/v1/events` - Create new event
- `GET /api/v1/events/{id}` - Get event details
- `PATCH /api/v1/events/{id}` - Update event description
- `DELETE /api/v1/events/{id}` - Delete event

### Helpdesk

- `POST /api/v1/helpdesk/chat` - Send message to chatbot
- `POST /api/v1/helpdesk/escalate` - Escalate to human agent

### Health Checks

- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed system health

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_auth.py
```

### Code Quality

```bash
# Format code
poetry run black app tests
poetry run isort app tests

# Lint code
poetry run flake8 app tests
poetry run mypy app

# Security scan
poetry run bandit -r app
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Security

This application implements comprehensive security measures:

- **Authentication**: OAuth2.0 password flow with JWT tokens
- **Encryption**: Passwords hashed with bcrypt, TLS for all communications
- **Input Validation**: Pydantic schemas for all inputs
- **Rate Limiting**: Protection against brute force attacks
- **CORS**: Configured for frontend access only
- **Security Headers**: HSTS, CSP, X-Frame-Options, etc.
- **Audit Logging**: All security events logged
- **OWASP Top 10**: Protection against common vulnerabilities

## Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY` and admin API key
- [ ] Generate and secure JWT keys
- [ ] Configure SSL/TLS certificates
- [ ] Set up email service for password reset
- [ ] Configure monitoring and logging
- [ ] Set `ENVIRONMENT=production` and `DEBUG=false`
- [ ] Review and adjust rate limits
- [ ] Set up database backups
- [ ] Configure firewall rules

### Docker Production Build

```bash
docker build -t ucc-event-manager-backend:latest .
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Ensure all tests pass
5. Submit a pull request

## License

[License information here]

## Support

For issues and questions:
- Check the API documentation at `/api/v1/docs`
- Review logs for error details
- Contact the development team

## Agentic Event Creation Feature

This feature allows users to create events by conversing naturally with the chatbot. The user can say something like "create an event for a barbecue this weekend", and the chatbot will extract the relevant details and create the event automatically.

### How It Works

1. The user makes a request to create an event in natural language
2. The Rasa NLU system recognizes the intent as `create_event_unstructured`
3. The LLM Entity Extractor component extracts entities from the message:
   - `event_title`: The title of the event (e.g., "barbecue")
   - `event_description`: Any description provided (e.g., "need to buy meat and vegetables")
   - `event_occurrence_text`: When the event should occur (e.g., "this weekend")
4. The custom action `action_create_event_from_llm` processes these entities:
   - Parses the occurrence text into a datetime using `dateparser`
   - Makes an authenticated API call to the backend to create the event
   - Provides user feedback about success or failure

### Configuration

The following environment variables are required:

- `BACKEND_API_URL`: URL of the backend API (default: "http://backend:8000/api/v1")
- `RASA_SERVICE_API_KEY`: API key for service-to-service authentication
- `OLLAMA_API_BASE`: URL of the Ollama LLM service
- `OLLAMA_MODEL`: The model to use for LLM-based extraction

Generate a secure random key for the service API key:
```bash
openssl rand -hex 32
```

### Security

Communication between the Rasa action server and the backend API is secured using API key authentication. The API key is passed in the `X-Service-API-Key` header.

### Testing

Test conversations are defined in `rasa/tests/conversation_tests.md`. Run the tests with:

```bash
docker-compose exec rasa rasa test
``` 