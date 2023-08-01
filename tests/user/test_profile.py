from fastapi import status

from client_requests import (
    request_profile,
    request_me,
)


async def test_profile(client, create_test_user):
    # User profile
    response = await request_profile(client, "username")
    assert response.json()["username"] == "username"
    assert response.status_code == status.HTTP_200_OK


async def test_bad_profile(client):
    # Unknown user profile
    response = await request_profile(client, "bad_username")
    assert response.json()["code"] == "user_not_found"
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_me(client, create_test_user):
    # Get own profile
    response = await request_me(client, create_test_user)
    assert response.json()["username"] == "username"
    assert response.status_code == status.HTTP_200_OK
