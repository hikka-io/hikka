from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from .database import get_session
from fastapi import Header, Query
from .models import User, Anime
from fastapi import Depends
from .errors import Abort
from app import constants

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


# Get anime by slug
async def get_anime(
    slug: str, session: AsyncSession = Depends(get_session)
) -> Anime:
    if not (anime := await get_anime_by_slug(session, slug)):
        raise Abort("anime", "not-found")

    return anime


# Check user auth token
def auth_required(
    oauth_skip: bool = False,
    permissions: list = [],
):
    async def auth(
        auth: str = Header(),
        session: AsyncSession = Depends(get_session),
    ) -> User:
        if not (token := await get_auth_token(session, auth)):
            raise Abort("auth", "invalid-token")

        if not token.user:
            raise Abort("auth", "user-not-found")

        if token.user.banned:
            raise Abort("auth", "banned")

        if not token.user.username and not oauth_skip:
            raise Abort("auth", "username-required")

        if not token.user.email and not oauth_skip:
            raise Abort("auth", "email-required")

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
