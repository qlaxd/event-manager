"""
Configuration management for UCC Event Manager.
Uses Pydantic settings for environment variable validation and type safety.
"""
import secrets
from typing import Any, List, Optional, Union
from pathlib import Path


from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation and type safety."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application Settings
    APP_NAME: str = "UCC Event Manager"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "DEBUG"
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    FRONTEND_URL: AnyHttpUrl = "http://localhost:5173"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:5173"]
    
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Any:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v
    
    # Security Settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    PASSWORD_RESET_EXPIRE_MINUTES: int = 60
    
    # Rasa Service API Key for machine-to-machine communication
    RASA_SERVICE_API_KEY: str = secrets.token_urlsafe(32)
    
    # JWT Keys
    JWT_PRIVATE_KEY_PATH: Optional[Path] = None
    JWT_PUBLIC_KEY_PATH: Optional[Path] = None
    JWT_PRIVATE_KEY: Optional[str] = None
    JWT_PUBLIC_KEY: Optional[str] = None
    
    @field_validator("JWT_PRIVATE_KEY", mode="before")
    def load_private_key(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v:
            return v
        key_path = info.data.get("JWT_PRIVATE_KEY_PATH") if info.data else None
        if key_path and Path(key_path).exists():
            return Path(key_path).read_text()
        return None
    
    @field_validator("JWT_PUBLIC_KEY", mode="before")
    def load_public_key(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v:
            return v
        key_path = info.data.get("JWT_PUBLIC_KEY_PATH") if info.data else None
        if key_path and Path(key_path).exists():
            return Path(key_path).read_text()
        return None
    
    # Database Settings
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_POOL_PRE_PING: bool = True
    DATABASE_ECHO: bool = False
    
    # Redis Settings
    REDIS_URL: Optional[str] = None
    
    # Email Settings
    SMTP_ENABLED: bool = True
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: EmailStr
    SMTP_FROM_NAME: str = "UCC Event Manager"
    SMTP_TLS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_AUTH_REQUESTS: int = 5
    RATE_LIMIT_AUTH_WINDOW: int = 900  # 15 minutes
    RATE_LIMIT_PASSWORD_RESET_REQUESTS: int = 3
    RATE_LIMIT_PASSWORD_RESET_WINDOW: int = 3600  # 1 hour
    RATE_LIMIT_GLOBAL_REQUESTS: int = 1000
    RATE_LIMIT_GLOBAL_WINDOW: int = 3600  # 1 hour
    
    # MFA Settings
    MFA_ISSUER_NAME: str = "UCC Event Manager"
    MFA_BACKUP_CODES_COUNT: int = 8
    MFA_TIME_WINDOW: int = 1
    
    # Password Policy
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_BCRYPT_ROUNDS: int = 12
    
    # Session Settings
    SESSION_LIFETIME_SECONDS: int = 86400  # 24 hours
    MAX_SESSIONS_PER_USER: int = 5
    
    # Rasa Chatbot Settings
    RASA_URL: Optional[str] = None
    RASA_TOKEN: Optional[str] = None
    
    # Twilio Settings (for voice helpdesk)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_ENABLED: bool = True
    
    # Admin Settings
    ADMIN_EMAIL: EmailStr
    ADMIN_API_KEY: str
    
    # Security Headers
    SECURITY_HEADERS: dict[str, str] = {
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
        #"Referrer-Policy": "strict-origin-when-cross-origin",
    }
    

        
    def get_rate_limit_string(self, limit_type: str) -> str:
        """Get rate limit string for slowapi."""
        if limit_type == "auth":
            return f"{self.RATE_LIMIT_AUTH_REQUESTS}/{self.RATE_LIMIT_AUTH_WINDOW}seconds"
        elif limit_type == "password_reset":
            return f"{self.RATE_LIMIT_PASSWORD_RESET_REQUESTS}/{self.RATE_LIMIT_PASSWORD_RESET_WINDOW}seconds"
        elif limit_type == "global":
            return f"{self.RATE_LIMIT_GLOBAL_REQUESTS}/{self.RATE_LIMIT_GLOBAL_WINDOW}seconds"
        else:
            raise ValueError(f"Unknown rate limit type: {limit_type}")


# Create a singleton instance
settings = Settings()


# Validate critical settings on startup
def validate_settings():
    """Validate critical settings on application startup."""
    if settings.ENVIRONMENT == "production":
        assert settings.SECRET_KEY != "your-secret-key-change-this-in-production", \
            "Secret key must be changed in production"
        assert settings.JWT_PRIVATE_KEY, "JWT private key is required in production"
        assert settings.JWT_PUBLIC_KEY, "JWT public key is required in production"
        assert not settings.DEBUG, "Debug mode must be disabled in production"
        assert settings.ADMIN_API_KEY != "generate-secure-admin-api-key", \
            "Admin API key must be changed in production" 