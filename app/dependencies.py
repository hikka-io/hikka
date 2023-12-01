from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Header, Query, Depends
from datetime import datetime, timedelta
from app.database import get_session
from app.utils import get_settings
from app.models import User, Anime
from typing import Annotated
from app.errors import Abort
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

    return user


# Get current pagination page
async def get_page(page: int = Query(gt=0, default=1)):
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


# Check user auth token
def auth_required(permissions: list = [], optional: bool = False):
    async def auth(
        auth_token: Annotated[str | None, Header(alias="auth")] = None,
        session: AsyncSession = Depends(get_session),
    ) -> User | None:
        error = None

        if not auth_token:
            error = Abort("auth", "missing-token")

        if not error and not (
            token := await get_auth_token(session, auth_token)
        ):
            error = Abort("auth", "invalid-token")

        if not error and not token.user:
            error = Abort("auth", "user-not-found")

        if not error and token.user.banned:
            error = Abort("auth", "banned")

        # If optional set to true folowing checks would fail silently by returning None
        # I really hate this if statement but idea of creating separade dependency
        # for optional auth I hate even more
        if error:
            if optional:
                return None
            else:
                raise error

        now = datetime.utcnow()

        if now > token.expiration:
            raise Abort("auth", "token-expired")

        # Simple check for permissions
        if len(permissions) > 0:
            role_permissions = constants.ROLES.get(token.user.role, [])

            has_permission = all(
                permission in role_permissions for permission in permissions
            )

            if not has_permission:
                raise Abort("permission", "denied")

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

    if settings.captcha["test"] and captcha == settings.captcha["test"]:
        return True

    if not await utils.check_cloudflare_captcha(
        captcha, settings.captcha["secret_key"]
    ):
        raise Abort("captcha", "invalid")

    return True
