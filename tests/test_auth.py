import pytest
from pprint import pprint


def request_signup(client, username, password, email):
    return client.post(
        "/auth/signup",
        json={
            "username": username,
            "password": password,
            "email": email,
        },
    )


async def test_short_username(client):
    # Min username lenght is 5 characters
    response = await request_signup(client, "abc", "password", "test@mail.com")

    assert response.json()["code"] == "validation_error"
    assert response.status_code == 422


async def test_long_username(client):
    # Max username lenght is 16 characters
    response = await request_signup(
        client, "abcdefghijklmnopq", "password", "test@mail.com"
    )

    assert response.json()["code"] == "validation_error"
    assert response.status_code == 422


async def test_start_number_username(client):
    # Username starting with number
    response = await request_signup(
        client, "1user", "password", "test@mail.com"
    )

    assert response.json()["code"] == "validation_error"
    assert response.status_code == 422


async def test_short_password(client):
    # Min password length is 8 characters
    response = await request_signup(client, "username", "abc", "test@mail.com")

    assert response.json()["code"] == "validation_error"
    assert response.status_code == 422


async def test_long_password(client):
    # Max password length is 64 characters
    response = await request_signup(
        client,
        "username",
        "abcdefghijklmnopqabcdefghijklmnopqabcdefghijklmnopqabcdefghijklmn",
        "test@mail.com",
    )

    assert response.json()["code"] == "validation_error"
    assert response.status_code == 422


async def test_bad_email(client):
    response = await request_signup(
        client, "username", "password", "badmail.com"
    )

    assert response.json()["code"] == "validation_error"
    assert response.status_code == 422
