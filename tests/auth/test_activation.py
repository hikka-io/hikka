from sqlalchemy import select, desc
from datetime import datetime
from app.models import Log
from fastapi import status
from app import constants

from client_requests import (
    request_activation_resend,
    request_activation,
)


async def test_activation_bad_token(client, create_test_user_not_activated):
    # Try bad activation token
    response = await request_activation(client, "BAD_TOKEN")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:activation_invalid"


async def test_activation_rate_limit(
    client, create_test_user_not_activated, get_test_token
):
    # Try resend activation request before previous one has expired
    response = await request_activation_resend(client, get_test_token)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:activation_valid"


async def test_activation_expired(
    client, test_session, create_test_user_not_activated
):
    # Get test user
    user = create_test_user_not_activated

    # Force expire activation token
    user.activation_expire = datetime.utcnow()
    test_session.add(user)
    await test_session.commit()

    # Test activation with expired token
    response = await request_activation(client, user.activation_token)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:activation_expired"


async def test_activation_resend(
    client, test_session, create_test_user_not_activated, get_test_token
):
    # Get test user
    user = create_test_user_not_activated

    old_activation_token = user.activation_token

    user.activation_expire = datetime.utcnow()
    test_session.add(user)
    await test_session.commit()

    # Resend activation request and generate new token
    response = await request_activation_resend(client, get_test_token)
    assert response.status_code == status.HTTP_200_OK

    # Make sure new token has been created
    await test_session.refresh(user)
    assert old_activation_token != user.activation_token

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_ACTIVATION_RESEND
    assert log.user == create_test_user_not_activated


async def test_activation(client, test_session, create_test_user_not_activated):
    # Get test user
    user = create_test_user_not_activated

    # Activate account
    response = await request_activation(client, user.activation_token)

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("secret") is not None

    # Make sure account has been activated and data cleaned
    await test_session.refresh(user)

    assert user.activation_expire is None
    assert user.activation_token is None
    assert user.email_confirmed is True

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_ACTIVATION
    assert log.user == create_test_user_not_activated
