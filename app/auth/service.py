from app.models import User, EmailMessage, AuthToken
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from .oauth_client import GoogleClient
from .utils import hashpwd, new_token
from .schemas import SignupArgs
from sqlalchemy import select
from app.errors import Abort
from fastapi import Request
from typing import Union
import config


async def get_user_by_activation(
    session: AsyncSession, token: str
) -> Union[User, None]:
    return await session.scalar(select(User).filter_by(activation_token=token))


async def get_user_by_email(
    session: AsyncSession, email: str
) -> Union[User, None]:
    return await session.scalar(select(User).filter_by(email=email))


async def get_user_by_reset(
    session: AsyncSession, token: str
) -> Union[User, None]:
    return await session.scalar(
        select(User).filter_by(password_reset_token=token)
    )


async def get_google_oauth_url(request: Request) -> str:
    client = GoogleClient(
        client_id=config.oauth["google"]["client_id"],
        client_secret=config.oauth["google"]["client_secret"],
    )

    redirect_uri = request.url_for("callback_google")

    return client.get_authorize_url(
        scope="openid email profile",
        redirect_uri=redirect_uri,
    )


async def get_google_oauth_info(request: Request, code: str) -> dict:
    try:
        client = GoogleClient(
            client_id=config.oauth["google"]["client_id"],
            client_secret=config.oauth["google"]["client_secret"],
        )

        token, _ = await client.get_access_token(
            code, redirect_uri=request.url_for("callback_google")
        )

        client = GoogleClient(
            client_id=config.oauth["google"]["client_id"],
            client_secret=config.oauth["google"]["client_secret"],
            access_token=token,
        )

        _, info = await client.user_info()
    except Exception:
        raise Abort("auth", "oauth-invalid-code")

    return info


async def create_user(session: AsyncSession, signup: SignupArgs) -> User:
    password_hash = hashpwd(signup.password)
    activation_token = new_token()
    now = datetime.utcnow()

    user = User(
        **{
            "activation_expire": now + timedelta(hours=3),
            "activation_token": activation_token,
            "password_hash": password_hash,
            "username": signup.username,
            "email": signup.email,
            "last_active": now,
            "created": now,
            "login": now,
        }
    )

    session.add(user)
    await session.commit()

    return user


async def create_email(
    session: AsyncSession, email_type: str, content: str, user: User
) -> EmailMessage:
    message = EmailMessage(
        **{
            "created": datetime.utcnow(),
            "content": content,
            "type": email_type,
            "user": user,
        }
    )

    session.add(message)
    await session.commit()

    return message


async def create_auth_token(session: AsyncSession, user: User) -> AuthToken:
    now = datetime.utcnow()

    # Update user login time
    user.login = now

    token = AuthToken(
        **{
            "expiration": now + timedelta(minutes=30),
            "secret": new_token(),
            "created": now,
            "user": user,
        }
    )

    session.add_all([user, token])
    await session.commit()

    return token


async def create_activation_token(session: AsyncSession, user: User) -> User:
    # Generate new token
    user.activation_expire = datetime.utcnow() + timedelta(hours=3)
    user.activation_token = new_token()

    session.add(user)
    await session.commit()

    return user


async def create_password_token(session: AsyncSession, user: User) -> User:
    # Generate new password reset token
    user.password_reset_expire = datetime.utcnow() + timedelta(hours=3)
    user.password_reset_token = new_token()

    session.add(user)
    await session.commit()

    return user


async def activate_user(session: AsyncSession, user: User) -> User:
    # Activate user and delete token
    user.activation_token = None
    user.activated = True

    session.add(user)
    await session.commit()

    return user


async def change_password(session: AsyncSession, user: User, new_password: str):
    # Set new password and delete reset token
    user.password_hash = hashpwd(new_password)
    user.password_reset_expire = None
    user.password_reset_token = None

    session.add(user)
    await session.commit()

    return user
