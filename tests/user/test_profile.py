from sqlalchemy import select
from app.models import User
from fastapi import status

from client_requests import (
    request_profile,
    request_signup,
    request_login,
    request_me,
)


async def test_profile(client, test_session):
    # Create new account
    response = await request_signup(
        client, "user@mail.com", "username", "password"
    )

    assert response.status_code == status.HTTP_200_OK

    # Get account and activate it
    user = await test_session.scalar(
        select(User).filter(User.email == "user@mail.com")
    )

    user.activated = True
    test_session.add(user)
    await test_session.commit()

    # Login
    response = await request_login(client, "user@mail.com", "password")
    assert response.status_code == status.HTTP_200_OK

    auth_token = response.json()["secret"]

    # Get own profile
    response = await request_me(client, auth_token)
    assert response.json()["username"] == "username"
    assert response.status_code == status.HTTP_200_OK

    # User profile
    response = await request_profile(client, "username")
    assert response.json()["username"] == "username"
    assert response.status_code == status.HTTP_200_OK

    # Unknown user profile
    response = await request_profile(client, "bad_username")
    assert response.json()["code"] == "user_not_found"
    assert response.status_code == status.HTTP_404_NOT_FOUND
