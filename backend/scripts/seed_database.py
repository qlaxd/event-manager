#!/usr/bin/env python3
"""
Database seeding script for UCC Event Manager.
Populates the database with test data using Factory Boy.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker, init_db
from app.models.user import User
from app.models.event import Event


async def clear_database():
    """Clear existing data from the database."""
    print("🗑️  Clearing existing data...")
    
    async with async_session_maker() as session:
        try:
            # Delete events first (foreign key constraint)
            from sqlalchemy import text
            await session.execute(text("DELETE FROM events"))
            await session.execute(text("DELETE FROM users"))
            await session.commit()
            print("✅ Database cleared successfully")
        except Exception as e:
            await session.rollback()
            print(f"❌ Error clearing database: {e}")
            raise


async def seed_users():
    """Seed users into the database."""
    print("👥 Seeding users...")
    
    # We need to import and create factory instances since Factory Boy doesn't handle async directly
    from tests.factories import (
        UserFactory, AdminUserFactory, InactiveUserFactory, MFAUserFactory
    )
    
    users_data = []
    
    # Create regular users
    for i in range(20):
        user_data = UserFactory.build()
        users_data.append(user_data)
    
    # Create admin users
    for i in range(3):
        admin_data = AdminUserFactory.build()
        users_data.append(admin_data)
    
    # Create inactive users
    for i in range(2):
        inactive_data = InactiveUserFactory.build()
        users_data.append(inactive_data)
    
    # Create MFA enabled users
    for i in range(5):
        mfa_data = MFAUserFactory.build()
        users_data.append(mfa_data)
    
    async with async_session_maker() as session:
        try:
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
            
            await session.commit()
            print(f"✅ Created {len(users_data)} users")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding users: {e}")
            raise


async def seed_events():
    """Seed events into the database."""
    print("📅 Seeding events...")
    
    from tests.factories import (
        EventFactory, PastEventFactory, HungarianEventFactory,
        WorkshopEventFactory, MeetingEventFactory, DeletedEventFactory
    )
    
    async with async_session_maker() as session:
        try:
            # Get existing users to assign events to them
            from sqlalchemy import select
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            if not users:
                print("❌ No users found. Please seed users first.")
                return
            
            events_data = []
            
            # Create various types of events and distribute them among users
            import random
            
            # Regular events
            for i in range(50):
                user = random.choice(users)
                event_data = EventFactory.build()
                event_data.user_id = user.id
                events_data.append(event_data)
            
            # Past events
            for i in range(30):
                user = random.choice(users)
                event_data = PastEventFactory.build()
                event_data.user_id = user.id
                events_data.append(event_data)
            
            # Hungarian events
            for i in range(25):
                user = random.choice(users)
                event_data = HungarianEventFactory.build()
                event_data.user_id = user.id
                events_data.append(event_data)
            
            # Workshop events
            for i in range(15):
                user = random.choice(users)
                event_data = WorkshopEventFactory.build()
                event_data.user_id = user.id
                events_data.append(event_data)
            
            # Meeting events
            for i in range(40):
                user = random.choice(users)
                event_data = MeetingEventFactory.build()
                event_data.user_id = user.id
                events_data.append(event_data)
            
            # Soft-deleted events
            for i in range(10):
                user = random.choice(users)
                event_data = DeletedEventFactory.build()
                event_data.user_id = user.id
                events_data.append(event_data)
            
            # Insert events into database
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
            print(f"✅ Created {len(events_data)} events")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding events: {e}")
            raise


async def main():
    """Main seeding function."""
    print("🌱 Starting database seeding...")
    
    try:
        # Initialize database (create tables if they don't exist)
        await init_db()
        print("✅ Database initialized")
        
        # Clear existing data
        await clear_database()
        
        # Seed data
        await seed_users()
        await seed_events()
        
        print("🎉 Database seeding completed successfully!")
        
        # Display summary
        async with async_session_maker() as session:
            from sqlalchemy import select, func
            
            user_count = await session.scalar(select(func.count(User.id)))
            event_count = await session.scalar(select(func.count(Event.id)))
            
            print(f"\n📊 Summary:")
            print(f"   👥 Users: {user_count}")
            print(f"   📅 Events: {event_count}")
            
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 