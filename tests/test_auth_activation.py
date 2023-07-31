from sqlalchemy import select
from datetime import datetime
from app.models import User
from fastapi import status

from client_requests import (
    request_activation_resend,
    request_activation,
    request_signup,
)


async def test_activation(client, test_session):
    # Create new account
    response = await request_signup(
        client, "user@mail.com", "username", "password"
    )

    assert response.status_code == status.HTTP_200_OK

    # Try bad activation token
    response = await request_activation(client, "BAD_TOKEN")
    assert response.json()["code"] == "auth_activation_invalid"
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Try resend activation request before previous one has expired
    response = await request_activation_resend(client, "user@mail.com")
    assert response.json()["code"] == "auth_activation_valid"
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Force expire activation token
    user = await test_session.scalar(
        select(User).filter(User.email == "user@mail.com")
    )

    expired_activation_token = user.activation_token
    assert expired_activation_token != None

    user.activation_expire = datetime.utcnow()
    test_session.add(user)
    await test_session.commit()

    # Test activation with expired token
    response = await request_activation(client, expired_activation_token)
    assert response.json()["code"] == "auth_activation_expired"
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Resend activation request and generate new token
    response = await request_activation_resend(client, "user@mail.com")
    assert response.status_code == status.HTTP_200_OK

    # Refresh user db record in order to obtain new activation token
    await test_session.refresh(user)
    new_activation_token = user.activation_token

    # Activate account
    response = await request_activation(client, new_activation_token)
    assert response.status_code == status.HTTP_200_OK

    # Make sure account has been activated and data cleaned
    await test_session.refresh(user)

    assert user.activation_expire == None
    assert user.activation_token == None
    assert user.activated == True
