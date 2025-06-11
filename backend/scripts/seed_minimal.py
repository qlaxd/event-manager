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
from sqlalchemy import select

from app.core.database import async_session_maker, init_db
from app.models.user import User
from app.models.event import Event


async def seed_minimal_data():
    """Seed minimal test data."""
    print("🌱 Creating minimal test data...")
    
    from tests.factories import UserFactory, AdminUserFactory, EventFactory, HungarianEventFactory
    
    async with async_session_maker() as session:
        try:
            # Check if users already exist
            existing_emails = set()
            existing_users_query = select(User.email)
            result = await session.execute(existing_users_query)
            existing_emails = {row[0] for row in result.all()}
            
            print(f"Found {len(existing_emails)} existing users")
            
            # Create a few users
            users_data = []
            
            # Only add users that don't already exist
            if "test@example.com" not in existing_emails:
                user1_data = UserFactory.build()
                user1_data.email = "test@example.com"
                user1_data.full_name = "Test User"
                users_data.append(user1_data)
                
            if "admin@example.com" not in existing_emails:
                admin_data = AdminUserFactory.build()
                admin_data.email = "admin@example.com"
                admin_data.full_name = "Admin User"
                users_data.append(admin_data)
                
            if "teszt@example.com" not in existing_emails:
                hu_user_data = UserFactory.build()
                hu_user_data.email = "teszt@example.com"
                hu_user_data.full_name = "Teszt Felhasználó"
                users_data.append(hu_user_data)
            
            # Add Lajko Levi user if it doesn't exist
            if "lajkolevi@protonmail.com" not in existing_emails:
                lajko_user_data = UserFactory.build()
                lajko_user_data.email = "lajkolevi@protonmail.com"
                lajko_user_data.full_name = "Lajkó Levente"
                users_data.append(lajko_user_data)
            
            # Insert users
            users = []
            existing_users = []
            
            # Get existing users for events
            if users_data:
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
            
            # If no new users were created, fetch existing ones for events
            if not users:
                # Get existing users for reference in events
                result = await session.execute(select(User).where(User.email.in_(["test@example.com", "admin@example.com", "teszt@example.com"])))
                existing_users = result.scalars().all()
                
                # If we have no existing users, we can't create events
                if not existing_users:
                    print("No users available to create events")
                    await session.commit()
                    print(f"✅ Added only new users from {len(users_data)} attempts")
                    return
            
            # Use either new users or existing users
            all_users = users if users else existing_users
            
            # Skip events if we already have users and events in the database
            if not users:
                # Check if we already have events
                events_count = await session.execute(select(Event).limit(1))
                if events_count.scalar_one_or_none():
                    print("Events already exist, skipping event creation")
                    await session.commit()
                    print(f"✅ No new data needed to be added")
                    return
            
            # Create a few events
            events_data = []
            
            # Map emails to user indices
            email_to_idx = {user.email: i for i, user in enumerate(all_users)}
            
            # Regular event for test user
            if "test@example.com" in email_to_idx:
                event1_data = EventFactory.build()
                event1_data.title = "Test Meeting"
                event1_data.description = "This is a test meeting for development purposes."
                event1_data.user_id = all_users[email_to_idx["test@example.com"]].id
                events_data.append(event1_data)
            
            # Hungarian event for Hungarian user
            if "teszt@example.com" in email_to_idx:
                event2_data = HungarianEventFactory.build()
                event2_data.user_id = all_users[email_to_idx["teszt@example.com"]].id
                events_data.append(event2_data)
            
            # Admin event
            if "admin@example.com" in email_to_idx:
                event3_data = EventFactory.build()
                event3_data.title = "Admin Review"
                event3_data.description = "Administrative review meeting."
                event3_data.user_id = all_users[email_to_idx["admin@example.com"]].id
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
            
            print(f"✅ Created {len(users_data)} new users and {len(events_data)} events")
            print("\n📋 Test accounts available:")
            print("   📧 test@example.com (password: password123)")
            print("   📧 admin@example.com (password: password123) - Admin")
            print("   📧 teszt@example.com (password: password123)")
            print("   📧 lajkolevi@protonmail.com (password: password123)")
            
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