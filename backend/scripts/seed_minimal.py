#!/usr/bin/env python3
"""
Minimal database seeding script for UCC Event Manager.
Creates just a few test users and events for quick testing.
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker, init_db
from app.models.user import User
from app.models.event import Event


async def seed_minimal_data():
    """Seed minimal test data."""
    print("🌱 Creating minimal test data...")
    
    from tests.factories import UserFactory, AdminUserFactory, EventFactory, HungarianEventFactory
    
    async with async_session_maker() as session:
        try:
            # Create a few users
            users_data = []
            
            # Regular user
            user1_data = UserFactory.build()
            user1_data.email = "test@example.com"
            user1_data.full_name = "Test User"
            users_data.append(user1_data)
            
            # Admin user
            admin_data = AdminUserFactory.build()
            admin_data.email = "admin@example.com"
            admin_data.full_name = "Admin User"
            users_data.append(admin_data)
            
            # Hungarian user
            hu_user_data = UserFactory.build()
            hu_user_data.email = "teszt@example.com"
            hu_user_data.full_name = "Teszt Felhasználó"
            users_data.append(hu_user_data)
            
            # Insert users
            users = []
            for user_data in users_data:
                user = User(
                    email=user_data.email,
                    full_name=user_data.full_name,
                    hashed_password=user_data.hashed_password,
                    is_active=user_data.is_active,
                    is_admin=user_data.is_admin,
                    mfa_enabled=user_data.mfa_enabled,
                    mfa_secret=user_data.mfa_secret,
                    password_changed_at=user_data.password_changed_at,
                    failed_login_attempts=user_data.failed_login_attempts,
                    locked_until=user_data.locked_until,
                    last_login_at=user_data.last_login_at,
                    last_login_ip=user_data.last_login_ip,
                    created_at=user_data.created_at,
                    updated_at=user_data.updated_at,
                    deleted_at=user_data.deleted_at,
                )
                session.add(user)
                users.append(user)
            
            await session.flush()  # Get user IDs
            
            # Create a few events
            events_data = []
            
            # Regular event for test user
            event1_data = EventFactory.build()
            event1_data.title = "Test Meeting"
            event1_data.description = "This is a test meeting for development purposes."
            event1_data.user_id = users[0].id
            events_data.append(event1_data)
            
            # Hungarian event for Hungarian user
            event2_data = HungarianEventFactory.build()
            event2_data.user_id = users[2].id
            events_data.append(event2_data)
            
            # Admin event
            event3_data = EventFactory.build()
            event3_data.title = "Admin Review"
            event3_data.description = "Administrative review meeting."
            event3_data.user_id = users[1].id
            events_data.append(event3_data)
            
            # Insert events
            for event_data in events_data:
                event = Event(
                    title=event_data.title,
                    occurrence=event_data.occurrence,
                    description=event_data.description,
                    user_id=event_data.user_id,
                    created_at=event_data.created_at,
                    updated_at=event_data.updated_at,
                    deleted_at=event_data.deleted_at,
                )
                session.add(event)
            
            await session.commit()
            
            print(f"✅ Created {len(users_data)} users and {len(events_data)} events")
            print("\n📋 Test accounts created:")
            print("   📧 test@example.com (password: password123)")
            print("   📧 admin@example.com (password: password123) - Admin")
            print("   📧 teszt@example.com (password: password123)")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding data: {e}")
            raise


async def main():
    """Main function."""
    print("🌱 Starting minimal database seeding...")
    
    try:
        # Initialize database
        await init_db()
        print("✅ Database initialized")
        
        # Seed minimal data
        await seed_minimal_data()
        
        print("🎉 Minimal seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 