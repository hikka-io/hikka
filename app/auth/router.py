from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from fastapi import APIRouter, Depends
from app.models import User, UserOAuth
from app.database import get_session
from typing import Tuple, Union
from app import constants
from . import service
from . import oauth


from .dependencies import (
    validate_activation_resend,
    validate_password_confirm,
    validate_password_reset,
    validate_set_username,
    validate_activation,
    validate_set_email,
    validate_provider,
    validate_signup,
    get_user_oauth,
    validate_login,
    get_oauth_info,
)

from .schemas import (
    ProviderUrlResponse,
    TokenResponse,
    UserResponse,
    UsernameArgs,
    SignupArgs,
    EmailArgs,
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/signup",
    response_model=UserResponse,
    summary="Signup",
)
async def signup(
    signup: SignupArgs = Depends(validate_signup),
    session: AsyncSession = Depends(get_session),
):
    # Create new user
    user = await service.create_user(session, signup)

    # Add activation email to database
    await service.create_email(
        session,
        constants.EMAIL_ACTIVATION,
        user.activation_token,
        user,
    )

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
)
async def login(
    user: User = Depends(validate_login),
    session: AsyncSession = Depends(get_session),
):
    return await service.create_auth_token(session, user)


@router.post(
    "/activation",
    response_model=UserResponse,
    summary="Activate account",
)
async def activation(
    user: User = Depends(validate_activation),
    session: AsyncSession = Depends(get_session),
):
    return await service.activate_user(session, user)


@router.post(
    "/activation/resend",
    response_model=UserResponse,
    summary="Resend activation link",
)
async def activation_resend(
    user: User = Depends(validate_activation_resend),
    session: AsyncSession = Depends(get_session),
):
    user = await service.create_activation_token(session, user)

    # Add new activation email to database
    await service.create_email(
        session,
        constants.EMAIL_ACTIVATION,
        user.activation_token,
        user,
    )

    return user


@router.post(
    "/password/reset",
    response_model=UserResponse,
    summary="Password reset request",
)
async def reset_password(
    user: User = Depends(validate_password_reset),
    session: AsyncSession = Depends(get_session),
):
    user = await service.create_password_token(session, user)

    # Add new password reset email to database
    await service.create_email(
        session,
        constants.EMAIL_PASSWORD_RESET,
        user.password_reset_token,
        user,
    )

    return user


@router.post(
    "/password/confirm",
    response_model=UserResponse,
    summary="Confirm password reset",
)
async def password_reset(
    confirm: Tuple[User, str] = Depends(validate_password_confirm),
    session: AsyncSession = Depends(get_session),
):
    return await service.change_password(session, *confirm)


@router.put(
    "/username",
    response_model=UserResponse,
    summary="Set a username",
)
async def username(
    args: UsernameArgs = Depends(validate_set_username),
    user: User = Depends(auth_required(oauth_skip=True)),
    session: AsyncSession = Depends(get_session),
):
    return await service.set_username(session, user, args.username)


@router.put(
    "/email",
    response_model=UserResponse,
    summary="Set a email",
)
async def email(
    args: EmailArgs = Depends(validate_set_email),
    user: User = Depends(auth_required(oauth_skip=True)),
    session: AsyncSession = Depends(get_session),
):
    return await service.set_email(session, user, args.email)


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
    oauth: Union[UserOAuth, None] = Depends(get_user_oauth),
    data: dict[str, str] = Depends(get_oauth_info),
    session: AsyncSession = Depends(get_session),
    provider: str = Depends(validate_provider),
):
    if not oauth:
        oauth = await service.create_oauth_user(session, provider, data)

    await service.update_oauth_timestamp(session, oauth)

    return await service.create_auth_token(session, oauth.user)
