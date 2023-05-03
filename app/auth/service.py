from app.models import User, EmailMessage, AuthToken
from datetime import datetime, timedelta
from .utils import hashpwd, new_token
from .schemas import SignupArgs


async def get_user_by_activation(token: str):
    return await User.filter(activation_token=token).first()


async def get_user_by_reset(token: str):
    return await User.filter(password_reset_token=token).first()


async def get_user_by_email(email: str):
    return await User.filter(email=email).first()


async def create_user(signup: SignupArgs) -> User:
    password_hash = hashpwd(signup.password)
    activation_token = new_token()
    now = datetime.utcnow()

    return await User.create(
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


async def create_email(
    email_type: str, content: str, user: User
) -> EmailMessage:
    return await EmailMessage.create(
        **{
            "created": datetime.utcnow(),
            "content": content,
            "type": email_type,
            "receiver": user,
        }
    )


async def create_token(user: User) -> AuthToken:
    now = datetime.utcnow()

    return await AuthToken.create(
        **{
            "expiration": now + timedelta(minutes=30),
            "secret": new_token(),
            "created": now,
            "user": user,
        }
    )
