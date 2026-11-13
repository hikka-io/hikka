from app.utils import is_valid_username
from sqlalchemy import select, desc
from app.models import Log, User
from fastapi import status
from app import constants

from client_requests import (
    request_oauth_post,
    request_oauth_url,
    request_me,
)


async def test_provider(client):
    response = await request_oauth_url(client, "google")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["url"] is not None


async def test_invalid_provider(client):
    response = await request_oauth_url(client, "qwerty123")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:invalid_provider"


async def test_valid_oauth_signup(client, mock_oauth_data, test_session):
    response = await request_oauth_post(client, "google", "code")

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("secret") is not None

    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    user = await test_session.scalar(select(User))
    assert log.log_type == constants.LOG_LOGIN_OAUTH
    assert log.data["provider"] == "google"
    assert log.user == user


async def test_signup_invalid_provider(client, mock_oauth_invalid_data):
    response = await request_oauth_post(client, "qwerty123", "code")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:invalid_provider"


async def test_signup_invalid_code(client, mock_oauth_invalid_data):
    response = await request_oauth_post(client, "google", "invalidcode")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:invalid_code"


async def test_signup_absent_code(client, mock_oauth_invalid_data):
    response = await request_oauth_post(client, "google")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_valid_oauth_login(client, mock_oauth_data, test_session):
    response = await request_oauth_post(client, "google", "code")

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("secret") is not None

    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_LOGIN_OAUTH
    assert log.data["provider"] == "google"


async def test_oauth_login_email_exists(
    client, create_test_user_oauth, mock_oauth_data
):
    response = await request_oauth_post(client, "google", "code")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:email_exists"


async def test_valid_oauth_username(client, mock_oauth_data):
    response = await request_oauth_post(client, "google", "code")

    # Check username created by oauth signup
    response = await request_me(client, response.json()["secret"])
    assert response.json()["username"] == "testuser"


async def test_valid_oauth_username_extra(
    client, create_test_user, mock_oauth_data
):
    response = await request_oauth_post(client, "google", "code")

    # Check username created by oauth signup
    response = await request_me(client, response.json()["secret"])
    assert response.json()["username"].startswith("testuser") is True
    assert len(response.json()["username"]) == 15


async def test_oauth_username_rules(client, mock_oauth_data):
    # Username made from email follows same rules as regular signup
    cases = [
        ("john.doe-99@mail.com", "john_doe_99"),
        ("1st.place@mail.com", "1st_place"),
        ("380991234567@mail.com", None),  # No letters
        ("admin@mail.com", None),  # Reserved
        ("abc@mail.com", None),  # Too short
    ]

    for index, (email, expected) in enumerate(cases):
        mock_oauth_data.return_value = {
            "email": email,
            "id": f"TEST_OAUTH_ID_{index}",
        }

        response = await request_oauth_post(client, "google", "code")
        assert response.status_code == status.HTTP_200_OK

        response = await request_me(client, response.json()["secret"])
        username = response.json()["username"]

        assert is_valid_username(username)

        # Random username is used when email can't give valid one
        if expected is None:
            assert username.startswith("user_")
            continue

        assert username == expected
