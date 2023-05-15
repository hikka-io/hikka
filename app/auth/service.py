from app.models import User, EmailMessage, AuthToken
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from .utils import hashpwd, new_token
from .schemas import SignupArgs
from sqlalchemy import select
from typing import Union


async def get_user_by_activation(token: str):
    return await User.filter(activation_token=token).first()


async def get_user_by_reset(token: str):
    return await User.filter(password_reset_token=token).first()


async def get_user_by_email(
    email: str, session: AsyncSession
) -> Union[User, None]:
    return await session.scalar(select(User).filter_by(email=email))


async def create_user(signup: SignupArgs, session: AsyncSession) -> User:
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
    email_type: str, content: str, user: User, session: AsyncSession
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


async def create_auth_token(user: User) -> AuthToken:
    now = datetime.utcnow()

    # Update user login time
    user.login = now

    await user.save()

    return await AuthToken.create(
        **{
            "expiration": now + timedelta(minutes=30),
            "secret": new_token(),
            "created": now,
            "user": user,
        }
    )


async def create_activation_token(user: User) -> User:
    # Generate new token
    user.activation_expire = datetime.utcnow() + timedelta(hours=3)
    user.activation_token = new_token()

    await user.save()

    return user


async def create_password_token(user: User) -> User:
    # Generate new password reset token
    user.password_reset_expire = datetime.utcnow() + timedelta(hours=3)
    user.password_reset_token = new_token()

    await user.save()

    return user


async def activate_user(user: User) -> User:
    # Activate user and delete token
    user.activation_token = None
    user.activated = True

    await user.save()

    return user


async def change_password(user: User, new_password: str):
    # Set new password and delete reset token
    user.password_hash = hashpwd(new_password)
    user.password_reset_expire = None
    user.password_reset_token = None

    await user.save()

    return user
