from app.models import User, UserOAuth, AuthToken
from app.auth.utils import hashpwd, new_token
from datetime import datetime, timedelta
from sqlalchemy import select
from app import constants
import aiofiles
import json


async def load_json(path):
    async with aiofiles.open(path, mode="r") as file:
        contents = await file.read()
        return json.loads(contents)


async def create_user(
    test_session,
    activated=True,
    username="testuser",
    email="user@mail.com",
    role=constants.ROLE_USER,
):
    now = datetime.utcnow()

    user = User(
        **{
            "activation_expire": datetime.utcnow() + timedelta(hours=3),
            "password_hash": hashpwd("password"),
            "activation_token": new_token(),
            "activated": activated,
            "username": username,
            "last_active": now,
            "created": now,
            "email": email,
            "role": role,
            "login": now,
        }
    )

    test_session.add(user)
    await test_session.commit()

    return user


async def create_oauth(test_session, user_id):
    now = datetime.utcnow()

    oauth = UserOAuth(
        **{
            "oauth_id": "test-id",
            "provider": "google",
            "user_id": user_id,
            "last_used": now,
            "created": now,
        }
    )

    test_session.add(oauth)
    await test_session.commit()

    return oauth


async def create_token(test_session, email, token_secret):
    now = datetime.utcnow()

    user = await test_session.scalar(select(User).filter(User.email == email))

    token = AuthToken(
        **{
            "expiration": now + timedelta(minutes=30),
            "secret": token_secret,
            "created": now,
            "user": user,
        }
    )

    test_session.add(token)
    await test_session.commit()

    return token
