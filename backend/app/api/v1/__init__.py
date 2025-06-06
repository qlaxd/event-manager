"""
API v1 routes for UCC Event Manager.
"""
from app.api.v1 import auth, events, health, helpdesk, users

__all__ = ["auth", "users", "events", "helpdesk", "health"] 