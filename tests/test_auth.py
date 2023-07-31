from sqlalchemy import select
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

    # Test activation
    # Test activation reset
    # Test password reset
    # Test login

    # user = await test_session.scalar(
    #     select(User).filter(User.email == "user@mail.com")
    # )

    # print(user.username)
