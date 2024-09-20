from app.models import User, UserOAuth, AuthToken, Client, AuthTokenRequest
from app.utils import pagination, pagination_dict, utcnow
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.schemas import UserResponse
from app.database import get_session
from app import constants
from typing import Tuple
from . import service
from . import oauth

from app.dependencies import (
    auth_token_required,
    check_captcha,
    auth_required,
    get_page,
    get_size,
)
from app.service import (
    create_activation_token,
    create_email,
    create_log,
)

from .dependencies import (
    validate_auth_token_request,
    validate_activation_resend,
    validate_password_confirm,
    validate_password_reset,
    validate_auth_token,
    validate_activation,
    validate_provider,
    validate_signup,
    get_user_oauth,
    validate_login,
    get_oauth_data,
    validate_client,
    validate_scope,
)

from .schemas import (
    AuthTokenInfoPaginationResponse,
    AuthTokenInfoResponse,
    TokenRequestResponse,
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
    dependencies=[Depends(check_captcha)],
)
async def login(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(validate_login),
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


@router.get(
    "/token/info",
    summary="Get token info",
    response_model=AuthTokenInfoResponse,
)
async def auth_info(token: AuthToken = Depends(auth_token_required)):
    return token


@router.post(
    "/token/request/{client_reference}",
    summary="Make token request for a third-party client",
    response_model=TokenRequestResponse,
)
async def request_token(
    client: Client = Depends(validate_client),
    scope: list[str] = Depends(validate_scope),
    user: User = Depends(auth_required(forbid_thirdparty=True)),
    session: AsyncSession = Depends(get_session),
):
    return await service.create_auth_token_request(session, user, client, scope)


@router.post(
    "/token",
    summary="Make token for a third-party client",
    response_model=TokenResponse,
)
async def third_party_auth_token(
    token_request: AuthTokenRequest = Depends(validate_auth_token_request),
    session: AsyncSession = Depends(get_session),
):
    await create_log(
        session,
        constants.LOG_LOGIN_THIRDPARTY,
        token_request.user,
        token_request.client_id,
        {"scope": token_request.scope},
    )
    return await service.create_auth_token_from_request(session, token_request)


@router.get(
    "/token/thirdparty",
    summary="List third-party auth tokens",
    response_model=AuthTokenInfoPaginationResponse,
)
async def third_party_auth_tokens(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(auth_required(forbid_thirdparty=True)),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    now = utcnow()

    total = await service.count_user_thirdparty_auth_tokens(session, user, now)
    tokens = await service.list_user_thirdparty_auth_tokens(
        session, user, offset, limit, now
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": tokens.all(),
    }


@router.delete(
    "/token/{token_reference}",
    summary="Revoke auth token",
    response_model=AuthTokenInfoResponse,
    dependencies=[Depends(auth_required(forbid_thirdparty=True))],
)
async def revoke_token(
    token: AuthToken = Depends(validate_auth_token),
    session: AsyncSession = Depends(get_session),
):
    return await service.revoke_auth_token(session, token)
