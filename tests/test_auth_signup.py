from sqlalchemy import select
from app.models import User
from fastapi import status

from client_requests import (
    request_signup,
    request_login,
)


async def test_signup(client, test_session):
    # Create new account
    response = await request_signup(
        client, "user@mail.com", "username", "password"
    )

    assert response.status_code == status.HTTP_200_OK

    # Login to not activated account
    response = await request_login(client, "user@mail.com", "password")
    assert response.json()["code"] == "auth_not_activated"
    assert response.status_code == status.HTTP_400_BAD_REQUEST

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
