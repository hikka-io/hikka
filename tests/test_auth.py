from sqlalchemy import select
from datetime import datetime
from app.models import User
from fastapi import status


def request_signup(client, email, username, password):
    return client.post(
        "/auth/signup",
        json={"email": email, "username": username, "password": password},
    )


def request_login(client, email, password):
    return client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )


def request_activation(client, token):
    return client.post(
        "/auth/activation",
        json={"token": token},
    )


def request_activation_resend(client, email):
    return client.post(
        "/auth/activation/resend",
        json={"email": email},
    )


def request_password_reset(client, email):
    return client.post(
        "/auth/password/reset",
        json={"email": email},
    )


def request_password_confirm(client, token, new_password):
    return client.post(
        "/auth/password/confirm",
        json={"token": token, "password": new_password},
    )


async def test_short_username(client):
    # Min username lenght is 5 characters
    response = await request_signup(client, "test@mail.com", "abc", "password")

    assert response.json()["code"] == "validation_error"
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_long_username(client):
    # Max username lenght is 16 characters
    response = await request_signup(
        client, "test@mail.com", "abcdefghijklmnopq", "password"
    )

    assert response.json()["code"] == "validation_error"
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_start_number_username(client):
    # Username starting with number
    response = await request_signup(
        client, "test@mail.com", "1user", "password"
    )

    assert response.json()["code"] == "validation_error"
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_short_password(client):
    # Min password length is 8 characters
    response = await request_signup(client, "test@mail.com", "username", "abc")

    assert response.json()["code"] == "validation_error"
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_long_password(client):
    # Max password length is 64 characters
    response = await request_signup(
        client,
        "username",
        "abcdefghijklmnopqabcdefghijklmnopqabcdefghijklmnopqabcdefghijklmn",
        "test@mail.com",
    )

    assert response.json()["code"] == "validation_error"
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_bad_email(client):
    response = await request_signup(
        client, "username", "password", "badmail.com"
    )

    assert response.json()["code"] == "validation_error"
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_login_not_fount(client):
    # Login to non existing account
    response = await request_login(client, "non-existing@mail.com", "password")

    assert response.json()["code"] == "auth_user_not_found"
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_signup_flow(client, test_session):
    # Create new account
    response = await request_signup(
        client, "user@mail.com", "username", "password"
    )

    assert response.status_code == status.HTTP_200_OK

    # Login to not activated account
    response = await request_login(client, "user@mail.com", "password")
    assert response.json()["code"] == "auth_not_activated"
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Request password reset for not activated account
    response = await request_password_reset(client, "user@mail.com")
    assert response.json()["code"] == "auth_not_activated"
    assert response.status_code == status.HTTP_400_BAD_REQUEST

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

    # Login with old password
    response = await request_login(client, "user@mail.com", "password")
    assert response.json()["code"] == "auth_invalid_password"
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Login
    response = await request_login(client, "user@mail.com", "new_password")
    assert response.status_code == status.HTTP_200_OK
