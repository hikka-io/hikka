from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, UserOAuth, Client
from app.dependencies import auth_required
from app.client.service import get_client
from app.database import get_session
from app.schemas import EmailArgs
from app.errors import Abort
from fastapi import Depends
from app import constants
from . import oauth
import uuid

from app.utils import (
    is_protected_username,
    get_settings,
    checkpwd,
    utcnow,
)

from app.service import (
    get_user_by_username,
    get_user_by_email,
)

from .service import (
    get_auth_token_request,
    get_user_by_activation,
    get_user_by_reset,
    get_oauth_by_id,
)

from .schemas import (
    ComfirmResetArgs,
    TokenRequestArgs,
    TokenProceedArgs,
    SignupArgs,
    LoginArgs,
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

    if user.role == constants.ROLE_DELETED:
        raise Abort("user", "deleted")

    return user


async def validate_signup(
    signup: SignupArgs, session: AsyncSession = Depends(get_session)
) -> SignupArgs:
    settings = get_settings()

    # Prevent using reserved usernames
    if is_protected_username(signup.username):
        raise Abort("auth", "invalid-username")

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

    if user.role == constants.ROLE_DELETED:
        raise Abort("user", "deleted")

    # Check password hash
    # TODO: add failed login attempts here
    if not checkpwd(login.password, user.password_hash):
        raise Abort("auth", "invalid-password")

    return user


async def validate_provider(provider: str) -> str:
    settings = get_settings()

    enabled_providers = [
        provider
        for provider in settings.oauth
        if settings.oauth[provider].enabled
    ]

    if provider not in enabled_providers:
        raise Abort("auth", "invalid-provider")

    return provider


async def get_oauth_data(
    args: CodeArgs,
    provider: str = Depends(validate_provider),
):
    if not (data := await oauth.get_user_data(provider, args.code)):
        raise Abort("auth", "invalid-code")

    return data


async def get_user_oauth(
    data: dict = Depends(get_oauth_data),
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

    if user.role == constants.ROLE_DELETED:
        raise Abort("user", "deleted")

    # Let's have it here just in case
    if not user.activation_expire:
        raise Abort("auth", "activation-expired")

    # Check if activation token still valid
    if user.activation_expire < utcnow():
        raise Abort("auth", "activation-expired")

    return user


async def validate_activation_resend(
    user: User = Depends(auth_required()),
) -> User:
    # Make sure user not yet activated
    if user.email_confirmed:
        raise Abort("auth", "already-activated")

    # Prevent sending new activation email if previous token still valid
    if user.activation_expire:
        if utcnow() < user.activation_expire:
            raise Abort("auth", "activation-valid")

    return user


async def validate_password_reset(
    user: User = Depends(body_email_user),
) -> User:
    # Prevent sending new password reset email if previous token still valid
    if user.password_reset_expire:
        if utcnow() < user.password_reset_expire:
            raise Abort("auth", "reset-valid")

    return user


async def validate_password_confirm(
    confirm: ComfirmResetArgs, session: AsyncSession = Depends(get_session)
):
    # Get user by reset token
    if not (user := await get_user_by_reset(session, confirm.token)):
        raise Abort("auth", "reset-invalid")

    if user.role == constants.ROLE_DELETED:
        raise Abort("user", "deleted")

    # Just in case
    if not user.password_reset_expire:
        raise Abort("auth", "reset-expired")

    # Make sure reset token is valid
    if utcnow() > user.password_reset_expire:
        raise Abort("auth", "reset-expired")

    return user, confirm.password


async def validate_client(
    client_reference: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> Client:
    if not (client := await get_client(session, client_reference)):
        raise Abort("auth", "client-not-found")

    return client


def validate_scope(request: TokenRequestArgs) -> list[str]:
    for scope in request.scope:
        if scope not in constants.ALL_SCOPES + list(constants.SCOPE_GROUPS):
            raise Abort("auth", "invalid-scope")

    if len(request.scope) == 0:
        raise Abort("auth", "scope-empty")

    return request.scope


async def validate_auth_token_request(
    args: TokenProceedArgs,
    session: AsyncSession = Depends(get_session),
):
    now = utcnow()

    if not (
        request := await get_auth_token_request(session, args.request_reference)
    ):
        raise Abort("auth", "invalid-token-request")

    if now > request.expiration:
        raise Abort("auth", "token-request-expired")

    if request.client.secret != args.client_secret:
        raise Abort("auth", "invalid-client-credentials")

    return request
