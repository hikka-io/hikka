from fastapi import APIRouter, Depends
from app.models import User
from app import constants
from app import display
from . import service

from .dependencies import (
    validate_activation_resend,
    validate_password_confirm,
    validate_password_reset,
    validate_activation,
    validate_signup,
    validate_login,
)

from .schemas import (
    TokenResponse,
    UserResponse,
    SignupArgs,
)


router = APIRouter(prefix="/auth")


@router.post("/signup", response_model=UserResponse)
async def signup(signup: SignupArgs = Depends(validate_signup)):
    # Create new user
    user = await service.create_user(signup)

    # Add activation email to database
    await service.create_email(
        constants.EMAIL_ACTIVATION, user.activation_token, user
    )

    return display.user(user)


@router.post("/login", response_model=TokenResponse)
async def login(user: User = Depends(validate_login)):
    # Create auth token
    token = await service.create_token(user)

    return display.token(token)


@router.post("/activation", response_model=UserResponse)
async def activation(user: User = Depends(validate_activation)):
    return display.user(user)


@router.post("/activation/resend", response_model=UserResponse)
async def activation_resend(user: User = Depends(validate_activation_resend)):
    # Add new activation email to database
    await service.create_email(
        constants.EMAIL_ACTIVATION, user.activation_token, user
    )

    return display.user(user)


@router.post("/password/reset", response_model=UserResponse)
async def reset_password(user: User = Depends(validate_password_reset)):
    # Add new password reset email to database
    await service.create_email(
        constants.EMAIL_PASSWORD_RESET, user.password_reset_token, user
    )

    return display.user(user)


@router.post("/password/confirm", response_model=UserResponse)
async def password_reset(user: User = Depends(validate_password_confirm)):
    return display.user(user)
