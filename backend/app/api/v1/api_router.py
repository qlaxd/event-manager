from fastapi import APIRouter
from app.api.v1.endpoints import auth, events, health, helpdesk, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(helpdesk.router, prefix="/helpdesk", tags=["Helpdesk"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
