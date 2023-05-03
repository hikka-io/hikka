from .utils import checkpwd, hashpwd, new_token
from datetime import datetime, timedelta
from fastapi import Body, Depends
from app.errors import Abort
from app.models import User
from pydantic import EmailStr
from . import service

from .schemas import (
    ComfirmResetArgs,
    SignupArgs,
    LoginArgs,
)


async def body_email_user(email: EmailStr = Body(embed=True)) -> User:
    # Get user by email
    if not (user := await service.get_user_by_email(email)):
        raise Abort("auth", "user-not-found")

    return user


async def validate_signup(signup: SignupArgs) -> SignupArgs:
    # Check if username is availaible
    if await service.get_user_by_username(signup.username):
        raise Abort("auth", "username-taken")

    # Check if email has been used
    if await service.get_user_by_email(signup.username):
        raise Abort("auth", "email-exists")

    return signup


async def validate_login(login: LoginArgs) -> User:
    # Find user by email
    if not (user := await service.get_user_by_email(login.email)):
        raise Abort("auth", "user-not-found")

    # Check password hash
    if not checkpwd(login.password, user.password_hash):
        raise Abort("auth", "invalid-password")

    # Make sure user is activated
    if not user.activated:
        raise Abort("auth", "not-activated")

    # Update user login time
    user.login = datetime.utcnow()
    await user.save()

    return user


async def validate_activation(token: str = Body(embed=True)) -> User:
    # Find user by activation token
    if not (user := await service.get_user_by_activation(token)):
        raise Abort("auth", "activation-invalid")

    # Check if activation token still valid
    if user.activation_expire < datetime.utcnow():
        raise Abort("auth", "activation-expired")

    # Activate user and delete token
    user.activation_token = None
    user.activated = True
    await user.save()

    return user


async def validate_activation_resend(
    user: User = Depends(body_email_user),
) -> User:
    # Make sure user not yet activated
    if user.activated:
        raise Abort("auth", "already-activated")

    # Get current UTC datetime
    now = datetime.utcnow()

    # Prevent sending new activation email if previous token still valid
    if datetime.utcnow() > user.activation_expire:
        raise Abort("auth", "activation-valid")

    # Generate new token
    user.activation_expire = now + timedelta(hours=3)
    user.activation_token = new_token()
    await user.save()

    return user


async def validate_password_reset(
    user: User = Depends(body_email_user),
) -> User:
    # Make sure user is activated
    if not user.activated:
        raise Abort("auth", "not-activated")

    # Prevent sending new password reset email if previous token still valid
    if datetime.utcnow() > user.activation_expire:
        raise Abort("auth", "reset-valid")

    # Generate new password reset token
    user.password_reset_expire = datetime.utcnow() + timedelta(hours=3)
    user.password_reset_token = new_token()
    await user.save()

    return user


async def validate_password_confirm(confirm: ComfirmResetArgs):
    # Get user by reset token
    if not (user := await service.get_user_by_reset(confirm.token)):
        raise Abort("auth", "reset-invalid")

    # Make sure reset token is valid
    if datetime.utcnow() > user.password_reset_expire:
        raise Abort("auth", "reset-expired")

    # Set new password and delete reset token
    user.password_hash = hashpwd(confirm.password)
    user.password_reset_expire = None
    user.password_reset_token = None
    await user.save()

    return user
