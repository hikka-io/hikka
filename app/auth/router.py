from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import check_captcha
from fastapi import APIRouter, Depends
from app.models import User, UserOAuth
from app.schemas import UserResponse
from app.database import get_session
from app import constants
from typing import Tuple
from . import service
from . import oauth

from app.service import (
    create_activation_token,
    create_email,
    create_log,
)

from .dependencies import (
    validate_activation_resend,
    validate_password_confirm,
    validate_password_reset,
    validate_activation,
    validate_provider,
    validate_signup,
    get_user_oauth,
    validate_login,
    get_oauth_data,
)

from .schemas import (
    ProviderUrlResponse,
    TokenResponse,
    SignupArgs,
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/signup",
    response_model=TokenResponse,
    summary="Signup",
)
async def signup(
    session: AsyncSession = Depends(get_session),
    signup: SignupArgs = Depends(validate_signup),
    _: bool = Depends(check_captcha),
):
    # Create new user
    user = await service.create_user(session, signup)

    # Add activation email to database
    await create_email(
        session,
        constants.EMAIL_ACTIVATION,
        user.activation_token,
        user,
    )

    await create_log(session, constants.LOG_SIGNUP, user)

    return await service.create_auth_token(session, user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
)
async def login(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(validate_login),
    _: bool = Depends(check_captcha),
):
    await create_log(session, constants.LOG_LOGIN, user)
    return await service.create_auth_token(session, user)


@router.post(
    "/activation",
    response_model=TokenResponse,
    summary="Activate account",
)
async def activation(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(validate_activation),
):
    await service.activate_user(session, user)
    await create_log(session, constants.LOG_ACTIVATION, user)
    return await service.create_auth_token(session, user)


@router.post(
    "/activation/resend",
    response_model=UserResponse,
    summary="Resend activation link",
)
async def activation_resend(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(validate_activation_resend),
):
    user = await create_activation_token(session, user)

    # Add new activation email to database
    await create_email(
        session,
        constants.EMAIL_ACTIVATION,
        user.activation_token,
        user,
    )

    await create_log(session, constants.LOG_ACTIVATION_RESEND, user)

    return user


@router.post(
    "/password/reset",
    response_model=UserResponse,
    summary="Password reset request",
)
async def reset_password(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(validate_password_reset),
):
    user = await service.create_password_token(session, user)

    # Add new password reset email to database
    await create_email(
        session,
        constants.EMAIL_PASSWORD_RESET,
        user.password_reset_token,
        user,
    )

    await create_log(session, constants.LOG_PASSWORD_RESET, user)

    return user


@router.post(
    "/password/confirm",
    response_model=TokenResponse,
    summary="Confirm password reset",
)
async def password_reset(
    session: AsyncSession = Depends(get_session),
    confirm: Tuple[User, str] = Depends(validate_password_confirm),
):
    user = await service.change_password(session, *confirm)
    await create_log(session, constants.LOG_PASSWORD_RESET_CONFIRM, user)
    return await service.create_auth_token(session, user)


@router.get(
    "/oauth/{provider}",
    response_model=ProviderUrlResponse,
    summary="Get a provider OAuth url",
)
async def provider_url(provider: str = Depends(validate_provider)):
    return await oauth.get_url(provider)


@router.post(
    "/oauth/{provider}",
    response_model=TokenResponse,
    summary="Get auth token using OAuth",
)
async def oauth_token(
    session: AsyncSession = Depends(get_session),
    oauth_user: UserOAuth | None = Depends(get_user_oauth),
    data: dict[str, str] = Depends(get_oauth_data),
    provider: str = Depends(validate_provider),
):
    if not oauth_user:
        oauth_user = await service.create_oauth_user(session, provider, data)

    await service.update_oauth_timestamp(session, oauth_user)

    await create_log(
        session,
        constants.LOG_LOGIN_OAUTH,
        oauth_user.user,
        data={"provider": provider},
    )

    return await service.create_auth_token(session, oauth_user.user)
