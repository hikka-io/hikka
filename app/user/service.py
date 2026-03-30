from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, desc
from datetime import timedelta
from app.utils import utcnow
from app import constants

from app.models import (
    Digest,
    Follow,
    User,
)


async def get_user_activity(session: AsyncSession, user: User) -> User:
    """Get user activity"""

    digest = await session.scalar(
        select(Digest).filter(
            Digest.name == constants.DIGEST_ACTIVITY, Digest.user == user
        )
    )

    if not digest:
        return []

    return digest.data


async def users_meilisearch(
    session: AsyncSession,
    meilisearch_result: dict,
):
    usernames = [user["username"] for user in meilisearch_result["list"]]

    # NOTE: we may need to preserve results order from Meilisearch here
    # For reference see anime_meilisearch_watch function

    return await session.scalars(
        select(User)
        .filter(User.username.in_(usernames))
        .order_by(desc(User.last_active))
    )


async def load_is_followed(
    session: AsyncSession, user: User, request_user: User
) -> User | None:
    user.is_followed = await session.scalar(
        select(
            exists().where(
                Follow.followed_user == user,
                Follow.user == request_user,
            )
        )
    )

    return user
