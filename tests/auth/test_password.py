from sqlalchemy import select
from datetime import datetime
from app.models import User
from fastapi import status

from client_requests import (
    request_password_confirm,
    request_password_reset,
)


async def test_password_reset_not_activated(
    client, test_session, create_test_user_not_activated
):
    # Request password reset for not activated account
    response = await request_password_reset(client, "user@mail.com")
    assert response.json()["code"] == "auth:not_activated"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_password_reset(client, test_session, create_test_user):
    # Get user
    user = await test_session.scalar(
        select(User).filter(User.email == "user@mail.com")
    )

    assert user.password_reset_expire is None
    assert user.password_reset_token is None

    # Request password reset
    response = await request_password_reset(client, "user@mail.com")
    assert response.status_code == status.HTTP_200_OK

    # Make sure reset token has been set
    await test_session.refresh(user)
    assert user.password_reset_token is not None


async def test_password_reset_rate_limit(
    client, test_session, create_test_user
):
    # Request password reset
    response = await request_password_reset(client, "user@mail.com")
    assert response.status_code == status.HTTP_200_OK

    # Request password reset again to check rate limit
    response = await request_password_reset(client, "user@mail.com")
    assert response.json()["code"] == "auth:reset_valid"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_password_reset_expired(client, test_session, create_test_user):
    # Request password reset
    response = await request_password_reset(client, "user@mail.com")
    assert response.status_code == status.HTTP_200_OK

    # Get user
    user = await test_session.scalar(
        select(User).filter(User.email == "user@mail.com")
    )

    user.password_reset_expire = datetime.utcnow()
    test_session.add(user)
    await test_session.commit()

    # Reset password with expired token
    response = await request_password_confirm(
        client, user.password_reset_token, "new_password"
    )

    assert response.json()["code"] == "auth:reset_expired"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_password_reset_confirm(client, test_session, create_test_user):
    # Request password reset
    response = await request_password_reset(client, "user@mail.com")
    assert response.status_code == status.HTTP_200_OK

    # Get user
    user = await test_session.scalar(
        select(User).filter(User.email == "user@mail.com")
    )

    # Reset password
    response = await request_password_confirm(
        client, user.password_reset_token, "new_password"
    )

    assert response.status_code == status.HTTP_200_OK

    # Get old password hash to make sure it has been changed
    old_password_hash = user.password_hash
    await test_session.refresh(user)

    assert old_password_hash != user.password_hash
    assert user.password_reset_expire is None
    assert user.password_reset_token is None
