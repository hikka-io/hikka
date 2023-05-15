from sqlalchemy.ext.asyncio import AsyncSession
from app.service import get_user_by_username
from app.database import get_session
from fastapi import Body, Depends
from datetime import datetime
from pydantic import EmailStr
from app.errors import Abort
from app.models import User
from .utils import checkpwd

from .service import (
    get_user_by_activation,
    get_user_by_email,
    get_user_by_reset,
)

from .schemas import (
    ComfirmResetArgs,
    SignupArgs,
    LoginArgs,
)


async def body_email_user(email: EmailStr = Body(embed=True)) -> User:
    # Get user by email
    if not (user := await get_user_by_email(email)):
        raise Abort("auth", "user-not-found")

    return user


async def validate_signup(
    signup: SignupArgs, session: AsyncSession = Depends(get_session)
) -> SignupArgs:
    # Check if username is availaible
    if await get_user_by_username(signup.username, session):
        raise Abort("auth", "username-taken")

    # Check if email has been used
    if await get_user_by_email(signup.username, session):
        raise Abort("auth", "email-exists")

    return signup


async def validate_login(login: LoginArgs) -> User:
    # Find user by email
    if not (user := await get_user_by_email(login.email)):
        raise Abort("auth", "user-not-found")

    # Check password hash
    if not checkpwd(login.password, user.password_hash):
        raise Abort("auth", "invalid-password")

    # Make sure user is activated
    if not user.activated:
        raise Abort("auth", "not-activated")

    return user


async def validate_activation(token: str = Body(embed=True)) -> User:
    # Find user by activation token
    if not (user := await get_user_by_activation(token)):
        raise Abort("auth", "activation-invalid")

    # Check if activation token still valid
    if user.activation_expire < datetime.utcnow():
        raise Abort("auth", "activation-expired")

    return user


async def validate_activation_resend(
    user: User = Depends(body_email_user),
) -> User:
    # Make sure user not yet activated
    if user.activated:
        raise Abort("auth", "already-activated")

    # Prevent sending new activation email if previous token still valid
    if datetime.utcnow() > user.activation_expire:
        raise Abort("auth", "activation-valid")

    return user


async def validate_password_reset(
    user: User = Depends(body_email_user),
) -> User:
    # Make sure user is activated
    if not user.activated:
        raise Abort("auth", "not-activated")

    # Prevent sending new password reset email if previous token still valid
    if datetime.utcnow() > user.password_reset_expire:
        raise Abort("auth", "reset-valid")

    return user


async def validate_password_confirm(confirm: ComfirmResetArgs):
    # Get user by reset token
    if not (user := await get_user_by_reset(confirm.token)):
        raise Abort("auth", "reset-invalid")

    # Make sure reset token is valid
    if datetime.utcnow() > user.password_reset_expire:
        raise Abort("auth", "reset-expired")

    return user, confirm.password
