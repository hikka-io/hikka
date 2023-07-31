from sqlalchemy import select
from datetime import datetime
from app.models import User
from fastapi import status

from client_requests import (
    request_password_confirm,
    request_password_reset,
    request_signup,
)


async def test_password_reset(client, test_session):
    # Create new account
    response = await request_signup(
        client, "user@mail.com", "username", "password"
    )

    assert response.status_code == status.HTTP_200_OK

    # Request password reset for not activated account
    response = await request_password_reset(client, "user@mail.com")
    assert response.json()["code"] == "auth_not_activated"
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Get account and activate it
    user = await test_session.scalar(
        select(User).filter(User.email == "user@mail.com")
    )

    user.activated = True
    test_session.add(user)
    await test_session.commit()

    # Request password reset
    response = await request_password_reset(client, "user@mail.com")
    assert response.status_code == status.HTTP_200_OK

    # Request password reset again to check rate limit
    response = await request_password_reset(client, "user@mail.com")
    assert response.json()["code"] == "auth_reset_valid"
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Force expire password reset token
    await test_session.refresh(user)

    expired_password_reset_token = user.password_reset_token
    assert expired_password_reset_token != None

    user.password_reset_expire = datetime.utcnow()
    test_session.add(user)
    await test_session.commit()

    # Reset password with expired token
    response = await request_password_confirm(
        client, expired_password_reset_token, "new_password"
    )

    assert response.json()["code"] == "auth_reset_expired"
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Request password reset
    response = await request_password_reset(client, "user@mail.com")
    assert response.status_code == status.HTTP_200_OK

    # Refresh db user to obtain reset token
    await test_session.refresh(user)

    new_password_reset_token = user.password_reset_token

    # Reset password
    response = await request_password_confirm(
        client, new_password_reset_token, "new_password"
    )

    assert response.status_code == status.HTTP_200_OK

    # Get old password hash to make sure it has been changed
    old_password_hash = user.password_hash
    await test_session.refresh(user)

    assert old_password_hash != user.password_hash
    assert user.password_reset_expire == None
    assert user.password_reset_token == None
