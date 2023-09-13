from sqlalchemy import select
from datetime import datetime
from app.models import User
from fastapi import status

from client_requests import (
    request_activation_resend,
    request_activation,
)


async def test_activation_bad_token(client, create_test_user_not_activated):
    # Try bad activation token
    response = await request_activation(client, "BAD_TOKEN")
    assert response.json()["code"] == "auth:activation_invalid"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_activation_rate_limit(client, create_test_user_not_activated):
    # Try resend activation request before previous one has expired
    response = await request_activation_resend(client, "user@mail.com")
    assert response.json()["code"] == "auth:activation_valid"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_activation_expired(
    client, test_session, create_test_user_not_activated
):
    # Force expire activation token
    user = await test_session.scalar(
        select(User).filter(User.email == "user@mail.com")
    )

    user.activation_expire = datetime.utcnow()
    test_session.add(user)
    await test_session.commit()

    # Test activation with expired token
    response = await request_activation(client, user.activation_token)
    assert response.json()["code"] == "auth:activation_expired"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_activation_resend(
    client, test_session, create_test_user_not_activated
):
    # Force expire activation token
    user = await test_session.scalar(
        select(User).filter(User.email == "user@mail.com")
    )

    old_activation_token = user.activation_token

    user.activation_expire = datetime.utcnow()
    test_session.add(user)
    await test_session.commit()

    # Resend activation request and generate new token
    response = await request_activation_resend(client, "user@mail.com")
    assert response.status_code == status.HTTP_200_OK

    # Make sure new token has been created
    await test_session.refresh(user)
    assert old_activation_token != user.activation_token


async def test_activation(client, test_session, create_test_user_not_activated):
    # Get test user
    user = await test_session.scalar(
        select(User).filter(User.email == "user@mail.com")
    )

    # Activate account
    response = await request_activation(client, user.activation_token)
    assert response.status_code == status.HTTP_200_OK

    # Make sure account has been activated and data cleaned
    await test_session.refresh(user)

    assert user.activation_expire is None
    assert user.activation_token is None
    assert user.activated is True
