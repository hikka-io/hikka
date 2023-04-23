from .responses import UserResponse, TokenResponse
from ..models import User, AuthToken, EmailMessage
from datetime import datetime, timedelta
from ..utils import hashpwd, checkpwd
from .args import JoinArgs, LoginArgs
from fastapi import APIRouter, Body
from pydantic import EmailStr
from ..errors import Abort
from .. import constants
from .. import display
import secrets

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/join")
async def join(
    args: JoinArgs
):
    # Check if username is availaible
    if await User.filter(username=args.username).first():
        raise Abort("auth", "username-taken")

    # Check if email is availaible
    if await User.filter(email=args.email).first():
        raise Abort("auth", "email-exists")

    # Create new user
    user = await User.create(**{
        "activation_expire": datetime.utcnow() + timedelta(hours=3),
        "activation_token": secrets.token_urlsafe(32),
        "password_hash": hashpwd(args.password),
        "last_active": datetime.utcnow(),
        "created": datetime.utcnow(),
        "login": datetime.utcnow(),
        "username": args.username,
        "email": args.email
    })

    # Add activation email to database
    await EmailMessage.create(**{
        "type": constants.EMAIL_ACTIVATION,
        "content": user.activation_token,
        "created": datetime.utcnow(),
        "receiver": user
    })

    # Return user info
    return display.user(user)

@router.post("/login", response_model=TokenResponse)
async def login(
    args: LoginArgs
):
    # Find user by email
    if not (user := await User.filter(email=args.email).first()):
        raise Abort("auth", "user-not-found")

    # Check password provided in request
    if not checkpwd(args.password, user.password_hash):
        raise Abort("auth", "invalid-password")

    # Make sure user is activated
    if not user.activated:
        raise Abort("auth", "not-activated")

    # Current time for token and login time
    now = datetime.utcnow()

    # Create auth token
    token = await AuthToken.create(**{
        "expiration": now + timedelta(minutes=30),
        "secret": secrets.token_urlsafe(32),
        "created": now,
        "user": user
    })

    # Update user login time
    user.login = now
    await user.save()

    # Return auth token
    return display.token(token)

@router.post("/activate", response_model=UserResponse)
async def activate(
    token: str = Body(embed=True),
):
    # Find user by activation token
    if not (user := await User.filter(activation_token=token).first()):
        raise Abort("auth", "activation-invalid")

    # Check if activation token still valid
    if user.activation_expire < datetime.utcnow():
        raise Abort("auth", "activation-expired")

    # Activate user and delete token
    user.activation_token = None
    user.activated = True
    await user.save()

    # Return user info
    return display.user(user)

@router.post("/resend/activation", response_model=UserResponse)
async def resend_activation(
    email: EmailStr = Body(embed=True)
):
    # Get user by email
    if not (user := await User.filter(email=email).first()):
        raise Abort("auth", "user-not-found")

    # Make sure user not yet activated
    if user.activated:
        raise Abort("auth", "already-activated")

    # Prevent sending new activation email if previous token still valid
    if datetime.utcnow() > user.activation_expire:
        raise Abort("auth", "activation-valid")

    # Generate new token
    user.activation_expire = datetime.utcnow() + timedelta(hours=3)
    user.activation_token = secrets.token_urlsafe(32)
    await user.save()

    # Add new activation email to database
    await EmailMessage.create(**{
        "type": constants.EMAIL_ACTIVATION,
        "content": user.activation_token,
        "created": datetime.utcnow(),
        "receiver": user
    })

    # Return user info
    return display.user(user)

@router.post("/reset", response_model=UserResponse)
async def reset_password(
    email: EmailStr = Body(embed=True)
):
    # Make sure user exists
    if not (user := await User.filter(email=email).first()):
        raise Abort("auth", "user-not-found")

    # Make sure user is activated
    if not user.activated:
        raise Abort("auth", "not-activated")

    # Prevent sending new password reset email if previous token still valid
    if datetime.utcnow() > user.activation_expire:
        raise Abort("auth", "reset-valid")

    # Generate new password reset token
    user.password_reset_token = secrets.token_urlsafe(32)
    user.password_reset_expire = datetime.utcnow() + timedelta(hours=3)
    await user.save()

    # Add new password reset email to database
    await EmailMessage.create(**{
        "type": constants.EMAIL_PASSWORD_RESET,
        "content": user.password_reset_token,
        "created": datetime.utcnow(),
        "receiver": user
    })

    # Return user info
    return display.user(user)

@router.post("/reset/confirm", response_model=UserResponse)
async def confirm_reset(
    password: str = Body(embed=True),
    token: str = Body(embed=True)
):
    # Get user by reset token
    if not (user := await User.filter(password_reset_token=token).first()):
        raise Abort("auth", "reset-invalid")

    # Make sure reset token is valid
    if datetime.utcnow() > user.password_reset_expire:
        raise Abort("auth", "reset-expired")

    # Set new password and delete reset token
    user.password_hash = hashpwd(password)
    user.password_reset_expire = None
    user.password_reset_token = None
    await user.save()

    # Return user info
    return display.user(user)
