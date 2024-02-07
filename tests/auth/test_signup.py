from client_requests import request_signup
from sqlalchemy import select, desc
from app.models import User, Log
from fastapi import status
from app import constants


async def test_signup(client, test_session):
    # Create new account
    response = await request_signup(
        client, "user@mail.com", "testuser", "password"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("secret") is not None

    # Get newly created account
    user = await test_session.scalar(
        select(User).filter(User.email == "user@mail.com")
    )

    assert user is not None

    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_SIGNUP
    assert log.user == user
    assert log.data == {}


async def test_signup_bad_email(client):
    # Create new account with duplicate email
    response = await request_signup(
        client, "user+email@mail.com", "testuser", "password"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_signup_duplicate_email(client, create_test_user):
    # Create new account with duplicate email
    response = await request_signup(
        client, "user@mail.com", "testuser2", "password"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:email_exists"


async def test_signup_duplicate_username(client, create_test_user):
    # Create new account with duplicate username
    response = await request_signup(
        client, "user2@mail.com", "testuser", "password"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:username_taken"


async def test_signup_protected_username(client):
    # Create new account with duplicate username
    response = await request_signup(
        client, "user@mail.com", "hikka", "password"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:invalid_username"
