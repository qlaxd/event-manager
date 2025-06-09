"""
User management endpoints for UCC Event Manager.
"""
import uuid
from fastapi import APIRouter, Depends, Response, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.user_service import UserService
from app.core.security import get_current_active_user, get_async_session
from schemas.user import UserRead, UserUpdate
from schemas.password import PasswordChange
from schemas.token import PaginatedSessionRead
from schemas.msg import Msg

router = APIRouter()


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get Current User Profile",
    description="Get the profile information for the currently authenticated user.",
    tags=["Users"],
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieves the profile of the currently authenticated user.
    """
    return current_user


@router.patch(
    "/me",
    response_model=UserRead,
    summary="Update Current User Profile",
    description="Update the profile information for the currently authenticated user.",
    tags=["Users"],
)
async def update_current_user_profile(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Updates the current user's profile. Can update `full_name`.
    """
    service = UserService(db)
    updated_user = await service.update_profile(current_user, user_update)
    return updated_user


@router.post(
    "/me/change-password",
    response_model=Msg,
    summary="Change User Password",
    description="Change the password for the currently authenticated user.",
    tags=["Users"],
)
async def change_current_user_password(
    password_data: PasswordChange,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Changes the user's password after verifying the current one.
    This action will log the user out of all other sessions.
    """
    service = UserService(db)
    await service.change_password(current_user, password_data)
    return {"msg": "Password changed successfully"}


@router.get(
    "/me/sessions",
    response_model=PaginatedSessionRead,
    summary="List User Sessions",
    description="Get a paginated list of active sessions for the current user.",
    tags=["Users"],
)
async def list_current_user_sessions(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """
    Retrieves a list of all active login sessions for the user.
    This can be used to identify unrecognized sessions.
    """
    service = UserService(db)
    sessions, total = await service.get_sessions(current_user, offset=offset, limit=limit)
    return PaginatedSessionRead(
        total=total,
        limit=limit,
        offset=offset,
        data=sessions,
    )


@router.delete(
    "/me/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke User Session",
    description="Revoke a specific active session for the current user (e.g., log out a device).",
    tags=["Users"],
)
async def delete_user_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Revokes a specific session by its ID, effectively logging out that session.
    A user can only revoke their own sessions.
    """
    service = UserService(db)
    await service.revoke_session(current_user, session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT) 