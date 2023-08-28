from app.auth.utils import hashpwd, new_token
from datetime import datetime, timedelta
from app.models import User, UserOAuth
import aiofiles
import json


async def load_json(path):
    async with aiofiles.open(path, mode="r") as file:
        contents = await file.read()
        return json.loads(contents)


async def create_user(
    test_session, activated=True, username="username", email="user@mail.com"
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
            "provider": "google",
            "oauth_id": "test-id",
            "last_used": now,
            "created": now,
            "user_id": user_id,
        }
    )

    test_session.add(oauth)
    await test_session.commit()

    return oauth
