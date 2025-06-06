# Data Model: UCC Event Manager

## 1. Overview
This document describes the database schema and data model for the UCC Event Manager system. The system uses PostgreSQL as the primary database with encryption at rest and secure password hashing to ensure data protection.

---

## 2. Entity Relationship Diagram (ERD)

```
┌─────────────────────────────────────┐
│                USERS                │
├─────────────────────────────────────┤
│ PK  id (UUID)                       │
│     email (VARCHAR, UNIQUE)         │
│     password_hash (VARCHAR)         │
│     full_name (VARCHAR)             │
│     mfa_secret (VARCHAR, NULL)      │
│     mfa_enabled (BOOLEAN)           │
│     is_active (BOOLEAN)             │
│     created_at (TIMESTAMP)          │
│     updated_at (TIMESTAMP)          │
└─────────────────────────────────────┘
                    │
                    │ 1:N
                    ▼
┌─────────────────────────────────────┐
│               EVENTS                │
├─────────────────────────────────────┤
│ PK  id (UUID)                       │
│ FK  user_id (UUID)                  │
│     title (VARCHAR)                 │
│     occurrence (TIMESTAMP)          │
│     description (TEXT, NULL)        │
│     created_at (TIMESTAMP)          │
│     updated_at (TIMESTAMP)          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│        PASSWORD_RESET_TOKENS        │
├─────────────────────────────────────┤
│ PK  token (VARCHAR)                 │
│ FK  user_id (UUID)                  │
│     expires_at (TIMESTAMP)          │
│     used (BOOLEAN)                  │
│     created_at (TIMESTAMP)          │
└─────────────────────────────────────┘
                    │
                    │ N:1
                    ▼
            ┌─────────────┐
            │    USERS    │
            └─────────────┘

┌─────────────────────────────────────┐
│           REFRESH_TOKENS            │
├─────────────────────────────────────┤
│ PK  id (UUID)                       │
│ FK  user_id (UUID)                  │
│     token_hash (VARCHAR)            │
│     expires_at (TIMESTAMP)          │
│     is_revoked (BOOLEAN)            │
│     created_at (TIMESTAMP)          │
└─────────────────────────────────────┘
                    │
                    │ N:1
                    ▼
            ┌─────────────┐
            │    USERS    │
            └─────────────┘

┌─────────────────────────────────────┐
│            AUDIT_LOGS               │
├─────────────────────────────────────┤
│ PK  id (UUID)                       │
│ FK  user_id (UUID, NULL)            │
│     action (VARCHAR)                │
│     resource_type (VARCHAR)         │
│     resource_id (VARCHAR, NULL)     │
│     ip_address (INET)               │
│     user_agent (TEXT, NULL)         │
│     details (JSONB, NULL)           │
│     created_at (TIMESTAMP)          │
└─────────────────────────────────────┘
```

---

## 3. Table Definitions

### 3.1 users
Primary table for user authentication and profile information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL, DEFAULT gen_random_uuid() | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address (used for login) |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt/Argon2 hashed password |
| full_name | VARCHAR(255) | NOT NULL | User's display name |
| mfa_secret | VARCHAR(32) | NULL | Base32-encoded TOTP secret for MFA |
| mfa_enabled | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether MFA is enabled for this user |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether the user account is active |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- `idx_users_email` - UNIQUE INDEX on email
- `idx_users_active` - INDEX on is_active

**Security Notes:**
- `password_hash` uses bcrypt with cost factor 12 or Argon2
- `mfa_secret` is encrypted at application level before storage
- `email` is case-insensitive (stored lowercase)

### 3.2 events
Table for storing user events with CRUD operations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL, DEFAULT gen_random_uuid() | Unique event identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY REFERENCES users(id) ON DELETE CASCADE | Owner of the event |
| title | VARCHAR(255) | NOT NULL | Event title (required) |
| occurrence | TIMESTAMP | NOT NULL | When the event occurs |
| description | TEXT | NULL | Optional event description |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Event creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- `idx_events_user_id` - INDEX on user_id
- `idx_events_occurrence` - INDEX on occurrence
- `idx_events_user_occurrence` - INDEX on (user_id, occurrence)

**Constraints:**
- Row-level security: Users can only access their own events
- `occurrence` must be a valid timestamp

### 3.3 password_reset_tokens
Table for managing password reset functionality.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| token | VARCHAR(255) | PRIMARY KEY, NOT NULL | URL-safe random token |
| user_id | UUID | NOT NULL, FOREIGN KEY REFERENCES users(id) ON DELETE CASCADE | User requesting reset |
| expires_at | TIMESTAMP | NOT NULL | Token expiration time (1 hour from creation) |
| used | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether token has been used |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Token creation timestamp |

**Indexes:**
- `idx_password_reset_user_id` - INDEX on user_id
- `idx_password_reset_expires` - INDEX on expires_at

**Security Notes:**
- Tokens are cryptographically secure random strings (32 bytes, base64url encoded)
- Tokens expire after 1 hour
- Tokens are single-use only
- Old tokens are automatically cleaned up

### 3.4 refresh_tokens
Table for managing JWT refresh tokens.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL, DEFAULT gen_random_uuid() | Unique token identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY REFERENCES users(id) ON DELETE CASCADE | Token owner |
| token_hash | VARCHAR(255) | NOT NULL, UNIQUE | SHA-256 hash of the refresh token |
| expires_at | TIMESTAMP | NOT NULL | Token expiration time |
| is_revoked | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether token has been revoked |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Token creation timestamp |

**Indexes:**
- `idx_refresh_tokens_hash` - UNIQUE INDEX on token_hash
- `idx_refresh_tokens_user_id` - INDEX on user_id
- `idx_refresh_tokens_expires` - INDEX on expires_at

**Security Notes:**
- Only hashes are stored, never plain tokens
- Tokens can be individually revoked
- Automatic cleanup of expired tokens

### 3.5 audit_logs (Optional)
Table for security auditing and monitoring.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL, DEFAULT gen_random_uuid() | Unique log entry identifier |
| user_id | UUID | NULL, FOREIGN KEY REFERENCES users(id) ON DELETE SET NULL | User who performed action (NULL for anonymous) |
| action | VARCHAR(50) | NOT NULL | Action performed (LOGIN, LOGOUT, CREATE_EVENT, etc.) |
| resource_type | VARCHAR(50) | NOT NULL | Type of resource affected (USER, EVENT, AUTH) |
| resource_id | VARCHAR(255) | NULL | ID of affected resource |
| ip_address | INET | NOT NULL | Client IP address |
| user_agent | TEXT | NULL | Client user agent string |
| details | JSONB | NULL | Additional action details |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When action occurred |

**Indexes:**
- `idx_audit_logs_user_id` - INDEX on user_id
- `idx_audit_logs_created_at` - INDEX on created_at
- `idx_audit_logs_action` - INDEX on action
- `idx_audit_logs_resource` - INDEX on (resource_type, resource_id)

---

## 4. Database Configuration

### 4.1 Connection Settings
```sql
-- Recommended PostgreSQL 15+ settings
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
random_page_cost = 1.1
```

### 4.2 Security Configuration
```sql
-- Enable row-level security
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own events
CREATE POLICY events_user_policy ON events
    FOR ALL TO authenticated_users
    USING (user_id = current_user_id());

-- Enable transparent data encryption (if supported)
-- This varies by PostgreSQL deployment
```

### 4.3 Performance Optimization
```sql
-- Partitioning for audit logs (by month)
CREATE TABLE audit_logs_2024_01 PARTITION OF audit_logs
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Automatic cleanup of old tokens
CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
RETURNS void AS $$
BEGIN
    DELETE FROM password_reset_tokens 
    WHERE expires_at < NOW() - INTERVAL '1 day';
    
    DELETE FROM refresh_tokens 
    WHERE expires_at < NOW() OR is_revoked = true;
END;
$$ LANGUAGE plpgsql;

-- Schedule cleanup (requires pg_cron extension)
SELECT cron.schedule('cleanup-tokens', '0 2 * * *', 'SELECT cleanup_expired_tokens();');
```

---

## 5. Data Migrations

### 5.1 Initial Schema Creation
```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    mfa_secret VARCHAR(32),
    mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create events table
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    occurrence TIMESTAMP NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create password_reset_tokens table
CREATE TABLE password_reset_tokens (
    token VARCHAR(255) PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create refresh_tokens table
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_events_user_id ON events(user_id);
CREATE INDEX idx_events_occurrence ON events(occurrence);
CREATE INDEX idx_events_user_occurrence ON events(user_id, occurrence);
CREATE INDEX idx_password_reset_user_id ON password_reset_tokens(user_id);
CREATE INDEX idx_password_reset_expires ON password_reset_tokens(expires_at);
CREATE INDEX idx_refresh_tokens_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at);
```

### 5.2 Seed Data
```sql
-- Insert demo users (passwords are hashed versions of 'password123')
INSERT INTO users (email, password_hash, full_name) VALUES
('admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiWhOj6/jcn6', 'System Administrator'),
('user1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiWhOj6/jcn6', 'John Doe'),
('user2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiWhOj6/jcn6', 'Jane Smith');
```

---

## 6. Data Validation Rules

### 6.1 Application-Level Validations
- **Email**: Must be valid email format, converted to lowercase
- **Password**: Minimum 8 characters, must contain uppercase, lowercase, number
- **Event Title**: 1-255 characters, no HTML tags
- **Event Occurrence**: Must be valid datetime, can be in past or future
- **Event Description**: Maximum 10,000 characters, basic HTML sanitization
- **MFA Secret**: Must be valid Base32 when present

### 6.2 Database Constraints
- **Foreign Key Integrity**: All references must exist
- **Unique Constraints**: Email addresses must be unique
- **NOT NULL**: Required fields cannot be empty
- **Check Constraints**: Custom business rules validation

---

## 7. Security Considerations

### 7.1 Encryption
- **At Rest**: PostgreSQL TDE or application-level encryption for sensitive fields
- **In Transit**: All connections use TLS 1.2+
- **Password Storage**: Bcrypt with cost factor 12 or Argon2
- **MFA Secrets**: Encrypted before database storage

### 7.2 Access Control
- **Row-Level Security**: Users can only access their own data
- **Database Users**: Separate users for application, admin, backup
- **Connection Limits**: Prevent resource exhaustion
- **Query Logging**: Log all modifications for audit trail

### 7.3 Data Retention
- **Password Reset Tokens**: Auto-delete after 24 hours
- **Refresh Tokens**: Auto-delete when expired or revoked
- **Audit Logs**: Retain for 90 days, then archive
- **User Data**: Soft delete with 30-day recovery period

---

*For API integration details, see [api-spec.md]. For security implementation, see [security.md].* 