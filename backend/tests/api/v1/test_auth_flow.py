"""
Tests for the authentication flow (/token and /refresh).
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import SecurityUtils
from tests.factories.user import UserFactory

# Mark all tests in this module as database-dependent
pytestmark = pytest.mark.asyncio


async def test_successful_token_refresh_flow(
    client: AsyncClient, 
    db_session: AsyncSession
) -> None:
    """
    Tests the full authentication flow:
    1. Create a user.
    2. Log in via /token endpoint to get tokens.
    3. Use the refresh token on the /refresh endpoint.
    4. Verify a new set of tokens is received.
    """
    # 1. Create a user
    password = "aVeryComplexP@ssword123"
    user = await UserFactory.create(
        hashed_password=SecurityUtils.get_password_hash(password)
    )

    # 2. Log in to get initial tokens
    login_data = {
        "username": user.email,
        "password": password,
    }
    login_response = await client.post(
        f"{settings.API_V1_PREFIX}/auth/token", 
        data=login_data
    )

    assert login_response.status_code == 200
    login_json = login_response.json()
    assert "access_token" in login_json
    assert "refresh_token" in login_json
    initial_refresh_token = login_json["refresh_token"]
    initial_access_token = login_json["access_token"]

    # 3. Use the refresh token to get a new access token
    refresh_data = {
        "grant_type": "refresh_token",
        "refresh_token": initial_refresh_token,
    }
    refresh_response = await client.post(
        f"{settings.API_V1_PREFIX}/auth/refresh",
        json=refresh_data
    )

    # 4. Verify the response
    assert refresh_response.status_code == 200, f"Refresh failed: {refresh_response.text}"
    refresh_json = refresh_response.json()
    
    assert "access_token" in refresh_json
    assert "refresh_token" in refresh_json
    
    # Ensure the new tokens are different from the old ones
    assert refresh_json["access_token"] != initial_access_token
    assert refresh_json["refresh_token"] != initial_refresh_token
    
    # Verify the new access token is valid by using it on a protected endpoint
    auth_headers = {"Authorization": f"Bearer {refresh_json['access_token']}"}
    profile_response = await client.get(
        f"{settings.API_V1_PREFIX}/users/me",
        headers=auth_headers
    )
    
    assert profile_response.status_code == 200
    profile_json = profile_response.json()
    assert profile_json["id"] == str(user.id)
    assert profile_json["email"] == user.email 