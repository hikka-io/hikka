from sqlalchemy.ext.asyncio import AsyncSession
from app.service import get_user_by_username
from app.dependencies import auth_required
from app.models import User, UserOAuth
from app.settings import get_settings
from app.database import get_session
from .oauth_client import OAuthError
from datetime import datetime
from app.errors import Abort
from fastapi import Depends
from .utils import checkpwd
from . import oauth

from .service import (
    get_user_by_activation,
    get_user_by_email,
    get_user_by_reset,
    get_oauth_by_id,
)

from .schemas import (
    ComfirmResetArgs,
    UsernameArgs,
    SignupArgs,
    LoginArgs,
    EmailArgs,
    TokenArgs,
    CodeArgs,
)


async def body_email_user(
    args: EmailArgs,
    session: AsyncSession = Depends(get_session),
) -> User:
    # Get user by email
    if not (user := await get_user_by_email(session, args.email)):
        raise Abort("auth", "user-not-found")

    return user


async def validate_set_username(
    args: UsernameArgs,
    user: User = Depends(auth_required(oauth_skip=True)),
    session: AsyncSession = Depends(get_session),
) -> UsernameArgs:
    if user.username:
        raise Abort("auth", "username-set")

    if await get_user_by_username(session, args.username):
        raise Abort("auth", "username-taken")

    return args


async def validate_set_email(
    args: EmailArgs,
    user: User = Depends(auth_required(oauth_skip=True)),
    session: AsyncSession = Depends(get_session),
) -> UsernameArgs:
    if user.email:
        raise Abort("auth", "email-set")

    if await get_user_by_email(session, args.email):
        raise Abort("auth", "email-exists")

    return args


async def validate_signup(
    signup: SignupArgs, session: AsyncSession = Depends(get_session)
) -> SignupArgs:
    settings = get_settings()

    # Check if username is availaible
    if await get_user_by_username(session, signup.username):
        raise Abort("auth", "username-taken")

    # Check if email has been used
    if await get_user_by_email(session, signup.email):
        raise Abort("auth", "email-exists")

    if len(settings.backend.auth_emails) > 0:
        if signup.email not in settings.backend.auth_emails:
            raise Abort("auth", "not-available")

    return signup


async def validate_login(
    login: LoginArgs, session: AsyncSession = Depends(get_session)
) -> User:
    # Find user by email
    if not (user := await get_user_by_email(session, login.email)):
        raise Abort("auth", "user-not-found")

    # Check password hash
    if not checkpwd(login.password, user.password_hash):
        raise Abort("auth", "invalid-password")

    return user


async def validate_provider(provider: str) -> str:
    settings = get_settings()

    enabled_providers = [p for p in settings.oauth if settings.oauth[p].enabled]

    if provider not in enabled_providers:
        raise Abort("auth", "invalid-provider")

    return provider


async def get_oauth_info(
    args: CodeArgs,
    provider: str = Depends(validate_provider),
):
    client = oauth.get_client(provider)
    data = None

    settings = get_settings()
    oauth_provider = settings.oauth.get(provider)

    try:
        otoken, _ = await client.get_access_token(
            args.code, oauth_provider["redirect_uri"]
        )

        client.access_token = otoken
        _, data = await client.user_info()

    except OAuthError:
        raise Abort("auth", "invalid-code")

    return data


async def get_user_oauth(
    data: dict[str, str] = Depends(get_oauth_info),
    provider: str = Depends(validate_provider),
    session: AsyncSession = Depends(get_session),
) -> UserOAuth | None:
    if not (oauth := await get_oauth_by_id(session, data["id"], provider)):
        email = data.get("email")

        if email and (await get_user_by_email(session, email)):
            raise Abort("auth", "email-exists")

    return oauth


async def validate_activation(
    args: TokenArgs,
    session: AsyncSession = Depends(get_session),
) -> User:
    # Find user by activation token
    if not (user := await get_user_by_activation(session, args.token)):
        raise Abort("auth", "activation-invalid")

    # Let's have it here just in case
    if not user.activation_expire:
        raise Abort("auth", "activation-expired")

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
    if user.activation_expire:
        if datetime.utcnow() < user.activation_expire:
            raise Abort("auth", "activation-valid")

    return user


async def validate_password_reset(
    user: User = Depends(body_email_user),
) -> User:
    # Prevent sending new password reset email if previous token still valid
    if user.password_reset_expire:
        if datetime.utcnow() < user.password_reset_expire:
            raise Abort("auth", "reset-valid")

    return user


async def validate_password_confirm(
    confirm: ComfirmResetArgs, session: AsyncSession = Depends(get_session)
):
    # Get user by reset token
    if not (user := await get_user_by_reset(session, confirm.token)):
        raise Abort("auth", "reset-invalid")

    # Just in case
    if not user.password_reset_expire:
        raise Abort("auth", "reset-expired")

    # Make sure reset token is valid
    if datetime.utcnow() > user.password_reset_expire:
        raise Abort("auth", "reset-expired")

    return user, confirm.password
