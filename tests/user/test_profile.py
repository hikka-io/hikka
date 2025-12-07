from fastapi import status

from app.models import User

from client_requests import (
    request_profile,
    request_me,
)


async def test_profile(client, create_test_user):
    # User profile
    response = await request_profile(client, "testuser")
    assert response.json()["username"] == "testuser"
    assert response.status_code == status.HTTP_200_OK

    # User profile with different case
    response = await request_profile(client, "TestUser")
    assert response.json()["username"] == "testuser"
    assert response.status_code == status.HTTP_200_OK


async def test_profile_reference(client, create_test_user: User):
    # User profile
    response = await request_profile(client, create_test_user.reference)
    print(response.json())  # ensure we know the response after test fail
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == create_test_user.username
    assert response.json()["reference"] == create_test_user.reference


async def test_bad_profile(client):
    # Unknown user profile
    response = await request_profile(client, "bad_username")
    assert response.json()["code"] == "user:not_found"
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_me(client, create_test_user, get_test_token):
    # Get own profile
    response = await request_me(client, get_test_token)
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == create_test_user.email
    assert response.status_code == status.HTTP_200_OK
