from app.models import User, EmailMessage, AuthToken, UserOAuth
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from sqlalchemy.orm import selectinload
from .utils import hashpwd, new_token
from .schemas import SignupArgs
from sqlalchemy import select
from typing import Union


async def get_user_by_activation(
    session: AsyncSession, token: str
) -> Union[User, None]:
    return await session.scalar(select(User).filter_by(activation_token=token))


async def get_user_by_email(
    session: AsyncSession, email: str
) -> Union[User, None]:
    return await session.scalar(select(User).filter_by(email=email))


async def get_oauth_by_id(
    session: AsyncSession, oauth_id: str, provider: str
) -> Union[UserOAuth, None]:
    return await session.scalar(
        select(UserOAuth)
        .filter_by(
            **{
                "provider": provider,
                "oauth_id": oauth_id,
            }
        )
        .options(selectinload(UserOAuth.user))
    )


async def get_user_by_username(
    session: AsyncSession, username: str
) -> Union[User, None]:
    return await session.scalar(select(User).filter_by(username=username))


async def get_user_by_reset(
    session: AsyncSession, token: str
) -> Union[User, None]:
    return await session.scalar(
        select(User).filter_by(password_reset_token=token)
    )


async def create_oauth_user(
    session: AsyncSession, provider: str, user_data: dict[str, str]
) -> UserOAuth:
    email = user_data.get("email")
    now = datetime.utcnow()

    user = User(
        **{
            "username": None,
            "password_hash": None,
            "email": email,
            "last_active": now,
            "created": now,
            "login": now,
            "activated": email is not None,
        }
    )

    oauth = UserOAuth(
        **{
            "user": user,
            "provider": provider,
            "oauth_id": user_data["id"],
            "last_used": now,
            "created": now,
        }
    )

    session.add(user)
    session.add(oauth)
    await session.commit()

    return oauth


async def update_oauth_timestamp(session: AsyncSession, oauth: UserOAuth):
    now = datetime.utcnow()
    oauth.last_used = now

    session.add(oauth)
    await session.commit()


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

    # After auth token will be valid only for 30 minutes
    # If unused it will expire
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


async def set_username(session: AsyncSession, user: User, username: str):
    user.username = username
    session.add(user)
    await session.commit()

    return user


async def set_email(session: AsyncSession, user: User, email: str):
    user.email = email
    session.add(user)
    await session.commit()

    return user


async def activate_user(session: AsyncSession, user: User) -> User:
    # Activate user and delete token
    user.activation_expire = None
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
