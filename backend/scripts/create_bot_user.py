#!/usr/bin/env python3
"""
Script to create a bot user in the database.
This user will be used by the chatbot to create events.
"""
import asyncio
import os
import sys
import uuid
from datetime import datetime

import asyncpg
from argparse import ArgumentParser
from passlib.context import CryptContext

# Setup password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bot user details - these can be adjusted as needed
BOT_USER_ID = "00000000-0000-0000-0000-000000000000"  # This matches the ID in actions.py
BOT_EMAIL = "bot@ucc-event-manager.local"
BOT_NAME = "Event Bot"
BOT_PASSWORD = pwd_context.hash("secure-bot-password")  # This password won't be used for login

def clean_db_url(url: str) -> str:
    """Convert SQLAlchemy URL to asyncpg format."""
    # If the URL starts with postgresql+asyncpg://, change it to postgresql://
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://")
    return url

async def create_bot_user(database_url: str):
    """Create a bot user in the database."""
    # Clean the database URL for asyncpg
    db_url = clean_db_url(database_url)
    print(f"Connecting to database: {db_url}")
    
    try:
        # Connect to the database
        conn = await asyncpg.connect(db_url)
        
        # Check if user already exists
        user_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM users WHERE id = $1)", 
            BOT_USER_ID
        )
        
        if user_exists:
            print(f"Bot user already exists with ID: {BOT_USER_ID}")
            await conn.close()
            return
        
        # Check if email already exists
        email_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM users WHERE email = $1)", 
            BOT_EMAIL
        )
        
        if email_exists:
            print(f"User with email {BOT_EMAIL} already exists. Please use a different email.")
            await conn.close()
            return
        
        # Create the bot user
        current_time = datetime.utcnow()
        await conn.execute("""
            INSERT INTO users (
                id, email, hashed_password, full_name, is_active, is_admin, 
                mfa_enabled, failed_login_attempts, created_at, updated_at, last_login_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        """, 
            BOT_USER_ID, BOT_EMAIL, BOT_PASSWORD, BOT_NAME,
            True, False, False, 0, current_time, current_time, None
        )
        
        print(f"Bot user created successfully with ID: {BOT_USER_ID}")
        print(f"Email: {BOT_EMAIL}")
        print(f"Name: {BOT_NAME}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error creating bot user: {e}")
        sys.exit(1)

def main():
    """Main entry point for the script."""
    parser = ArgumentParser(description="Create a bot user in the database.")
    parser.add_argument(
        "--database-url", 
        type=str, 
        default=os.environ.get("DATABASE_URL", "postgresql://postgres:password@localhost:5432/ucc_events"),
        help="Database URL (default: from DATABASE_URL environment variable)"
    )
    
    args = parser.parse_args()
    
    # Run the async function
    asyncio.run(create_bot_user(args.database_url))

if __name__ == "__main__":
    main() 