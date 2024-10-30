from app.models import User, UserOAuth, AuthToken, Client
from app.utils import new_token, hashpwd, utcnow
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
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
    now = utcnow()

    user = User(
        **{
            "activation_expire": utcnow() + timedelta(hours=3),
            "password_hash": hashpwd("password"),
            "activation_token": new_token(),
            "email_confirmed": activated,
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
    now = utcnow()

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


async def create_token(
    test_session, email, token_secret, client: Client = None
):
    now = utcnow()

    user = await test_session.scalar(select(User).filter(User.email == email))

    token = AuthToken(
        **{
            "expiration": now + timedelta(minutes=30),
            "secret": token_secret,
            "created": now,
            "user": user,
            "client": client,
        }
    )

    test_session.add(token)
    await test_session.commit()

    return token


async def create_client(
    session: AsyncSession,
    user: User,
    secret: str,
    name: str = "TestClient",
    description: str = "Test client",
    endpoint: str = "hikka://auth/",
    verified: bool = False,
):
    now = utcnow()
    client = Client(
        **{
            "secret": secret,
            "name": name,
            "description": description,
            "endpoint": endpoint,
            "verified": verified,
            "user": user,
            "created": now,
            "updated": now,
        }
    )

    session.add(client)
    await session.commit()

    return client
