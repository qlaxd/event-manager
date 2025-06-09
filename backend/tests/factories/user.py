"""
User factory for generating test data.
"""
import factory
from datetime import datetime, timezone
from faker import Faker

from app.models.user import User
from app.core.security import SecurityUtils

fake = Faker(['hu_HU', 'en_US'])


class UserFactory(factory.Factory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
    
    # Basic user information
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    full_name = factory.LazyFunction(lambda: fake.name())
    hashed_password = factory.LazyFunction(lambda: SecurityUtils.get_password_hash("password123"))
    
    # Account status
    is_active = True
    is_admin = False
    
    # MFA fields
    mfa_enabled = False
    mfa_secret = None
    
    # Password security
    password_changed_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    failed_login_attempts = 0
    locked_until = None
    
    # Login tracking
    last_login_at = factory.LazyFunction(lambda: fake.date_time_this_year(tzinfo=timezone.utc))
    last_login_ip = factory.LazyFunction(lambda: fake.ipv4())
    
    # Timestamps
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    
    # Soft delete
    deleted_at = None


class AdminUserFactory(UserFactory):
    """Factory for creating Admin User instances."""
    
    email = factory.Sequence(lambda n: f"admin{n}@example.com")
    full_name = factory.LazyFunction(lambda: f"Admin {fake.last_name()}")
    is_admin = True


class InactiveUserFactory(UserFactory):
    """Factory for creating Inactive User instances."""
    
    email = factory.Sequence(lambda n: f"inactive{n}@example.com")
    is_active = False


class MFAUserFactory(UserFactory):
    """Factory for creating User instances with MFA enabled."""
    
    email = factory.Sequence(lambda n: f"mfa_user{n}@example.com")
    mfa_enabled = True
    mfa_secret = factory.LazyFunction(lambda: fake.pystr(min_chars=32, max_chars=32).upper())
