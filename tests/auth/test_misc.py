from fastapi import status

from client_requests import (
    request_signup,
    request_login,
)


async def test_short_username(client):
    # Min username lenght is 5 characters
    response = await request_signup(client, "test@mail.com", "abc", "password")

    assert response.json()["code"] == "system:validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_long_username(client):
    # Max username lenght is 16 characters
    response = await request_signup(
        client, "test@mail.com", "abcdefghijklmnopq", "password"
    )

    assert response.json()["code"] == "system:validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_start_number_username(client):
    # Username starting with number
    response = await request_signup(
        client, "test@mail.com", "1user", "password"
    )

    assert response.json()["code"] == "system:validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_short_password(client):
    # Min password length is 8 characters
    response = await request_signup(client, "test@mail.com", "username", "abc")

    assert response.json()["code"] == "system:validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_long_password(client):
    # Max password length is 64 characters
    response = await request_signup(
        client,
        "username",
        "abcdefghijklmnopqabcdefghijklmnopqabcdefghijklmnopqabcdefghijklmn",
        "test@mail.com",
    )

    assert response.json()["code"] == "system:validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_bad_email(client):
    response = await request_signup(
        client, "username", "password", "badmail.com"
    )

    assert response.json()["code"] == "system:validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_login_not_fount(client):
    # Login to non existing account
    response = await request_login(client, "non-existing@mail.com", "password")

    assert response.json()["code"] == "auth:user_not_found"
    assert response.status_code == status.HTTP_404_NOT_FOUND
