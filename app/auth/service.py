from app.models import User, EmailMessage, AuthToken, UserOAuth
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from sqlalchemy.orm import selectinload
from .utils import hashpwd, new_token
from .schemas import SignupArgs
from sqlalchemy import select
from app import constants
import secrets


async def get_user_by_activation(
    session: AsyncSession, token: str
) -> User | None:
    return await session.scalar(
        select(User).filter(User.activation_token == token)
    )


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    return await session.scalar(select(User).filter(User.email == email))


async def get_oauth_by_id(
    session: AsyncSession, oauth_id: str, provider: str
) -> UserOAuth | None:
    return await session.scalar(
        select(UserOAuth)
        .filter(
            UserOAuth.provider == provider,
            UserOAuth.oauth_id == oauth_id,
        )
        .options(selectinload(UserOAuth.user))
    )


async def get_user_by_username(
    session: AsyncSession, username: str
) -> User | None:
    return await session.scalar(select(User).filter(User.username == username))


async def get_user_by_reset(session: AsyncSession, token: str) -> User | None:
    return await session.scalar(
        select(User).filter(User.password_reset_token == token)
    )


async def create_oauth_user(
    session: AsyncSession, provider: str, user_data: dict[str, str]
) -> UserOAuth:
    email = user_data.get("email")
    now = datetime.utcnow()

    # I really hate this part of code
    # but we need it for better user experience
    # when new account is created via oauth
    username = email.split("@")[0] if email else secrets.token_urlsafe(4)

    while True:
        if not (await get_user_by_username(session, username)):
            break

        username += "-" + secrets.token_urlsafe(4)

    user = User(
        **{
            "activated": email is not None,
            "role": constants.ROLE_USER,
            "password_hash": None,
            "username": username,
            "last_active": now,
            "email": email,
            "created": now,
            "login": now,
        }
    )

    oauth = UserOAuth(
        **{
            "oauth_id": user_data["id"],
            "provider": provider,
            "last_used": now,
            "created": now,
            "user": user,
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
            "role": constants.ROLE_NOT_ACTIVATED,
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

    # Only set user role if it's not activated
    if user.role == constants.ROLE_NOT_ACTIVATED:
        user.role = constants.ROLE_USER

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
