from fastapi import Header, Cookie, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Anime, AuthToken
from app.database import get_session
from app.utils import get_settings
from datetime import timedelta
from typing import Annotated
from app.errors import Abort
from app.utils import utcnow
from app import constants
from app import utils

from .service import (
    get_user_by_username,
    get_anime_by_slug,
    get_auth_token,
)


# Get user by username
async def get_user(
    username: str, session: AsyncSession = Depends(get_session)
) -> User:
    if not (user := await get_user_by_username(session, username)):
        raise Abort("user", "not-found")

    if user.role == constants.ROLE_DELETED:
        raise Abort("user", "deleted")

    return user


# Get current pagination page
async def get_page(page: int = Query(gt=0, le=10000, default=1)):
    return page


# Get current pagination size
async def get_size(
    size: int = Query(
        ge=1,
        le=100,
        default=constants.SEARCH_RESULT_SIZE,
    )
):
    return size


# Get anime by slug
async def get_anime(
    slug: str, session: AsyncSession = Depends(get_session)
) -> Anime:
    if not (anime := await get_anime_by_slug(session, slug)):
        raise Abort("anime", "not-found")

    return anime


# Get auth token either from header or cookies
async def get_request_auth_token(
    header_auth: Annotated[str | None, Header(alias="auth")] = None,
    cookie_auth: Annotated[str | None, Cookie(alias="auth")] = None,
) -> str | None:
    return header_auth if header_auth else cookie_auth


async def _auth_token_or_abort(
    session: AsyncSession = Depends(get_session),
    token: str | None = Depends(get_request_auth_token),
) -> Abort | AuthToken:
    now = utcnow()

    if not token:
        return Abort("auth", "missing-token")

    token = await get_auth_token(session, token)

    if not token:
        return Abort("auth", "invalid-token")

    if not token.user:
        return Abort("auth", "user-not-found")

    if token.user.banned:
        return Abort("auth", "banned")

    if now > token.expiration:
        return Abort("auth", "token-expired")

    token.used = now
    await session.commit()

    return token


async def auth_token_required(
    token: AuthToken | Abort = Depends(_auth_token_or_abort),
) -> AuthToken:
    if isinstance(token, Abort):
        raise token

    return token


async def auth_token_optional(
    token: AuthToken | Abort = Depends(_auth_token_or_abort),
) -> AuthToken | None:
    if isinstance(token, Abort):
        return None

    return token


# Check user auth token
def auth_required(
    permissions: list = None,
    scope: list = None,
    forbid_thirdparty: bool = False,
    optional: bool = False,
):
    """
    Authorization dependency with permission check

    If optional set to True and token not provided or invalid - returns None
    If optional set to False and token not provided or invalid - raises abort

    If token provided and valid - returns user from token
    """
    if not permissions:
        permissions = []

    if not scope:
        scope = []

    scope = utils.resolve_scope_groups(scope)

    async def auth(
        token: AuthToken | Abort = Depends(_auth_token_or_abort),
        session: AsyncSession = Depends(get_session),
    ) -> User | None:
        if isinstance(token, Abort):
            # If authorization is optional - ignore abort and return None
            if optional:
                return None

            # If authorization is required - raise abort
            raise token

        now = utcnow()

        # Check requested permissions here
        if not utils.check_user_permissions(token.user, permissions):
            raise Abort("permission", "denied")

        if forbid_thirdparty and token.client:
            raise Abort("permission", "denied")

        if not utils.check_token_scope(token, scope):
            raise Abort("permission", "denied")

        if token.user.role == constants.ROLE_DELETED:
            raise Abort("user", "deleted")

        # After each authenticated request token expiration will be reset
        token.expiration = now + timedelta(days=7)
        token.user.last_active = now

        session.add(token)
        await session.commit()

        return token.user

    return auth


# Validate captcha
async def check_captcha(
    captcha: Annotated[str, Header(alias="captcha")]
) -> bool:
    settings = get_settings()

    if not captcha:
        raise Abort("captcha", "invalid")

    if settings.captcha.get("test") and captcha == settings.captcha["test"]:
        return True

    if not await utils.check_cloudflare_captcha(
        captcha, settings.captcha["secret_key"]
    ):
        raise Abort("captcha", "invalid")

    return True
