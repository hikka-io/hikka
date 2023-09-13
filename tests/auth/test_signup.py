from client_requests import request_signup
from sqlalchemy import select
from app.models import User
from fastapi import status


async def test_signup(client, test_session):
    # Create new account
    response = await request_signup(
        client, "user@mail.com", "username", "password"
    )

    assert response.status_code == status.HTTP_200_OK

    # Get newly created account
    user = await test_session.scalar(
        select(User).filter(User.email == "user@mail.com")
    )

    assert user is not None


async def test_signup_duplicate_email(client, create_test_user):
    # Create new account with duplicate email
    response = await request_signup(
        client, "user@mail.com", "username2", "password"
    )

    assert response.json()["code"] == "auth:email_exists"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_signup_duplicate_username(client, create_test_user):
    # Create new account with duplicate username
    response = await request_signup(
        client, "user2@mail.com", "username", "password"
    )

    assert response.json()["code"] == "auth:username_taken"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
