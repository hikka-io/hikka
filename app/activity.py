from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from sqlalchemy import select
from uuid import UUID

from app.models import (
    Activity,
    Anime,
    User,
)


async def create_activity(
    session: AsyncSession,
    activity_type: str,
    target_id: UUID,
    user: User,
    data: dict = {},
):
    now = datetime.utcnow()

    activity = Activity(
        **{
            "activity_type": activity_type,
            "target_id": target_id,
            "updated": now,
            "created": now,
            "user": user,
            "data": data,
        }
    )

    session.add(activity)
    await session.commit()

    return activity


async def favourite_anime_add(
    session: AsyncSession,
    target: Anime,
    user: User,
):
    threshold = datetime.utcnow() - timedelta(days=1)
    activity_type = "favourite_anime"

    if not (
        activity := await session.scalar(
            select(Activity).filter(
                Activity.created > threshold,
                Activity.activity_type == activity_type,
                Activity.target_id == target.id,
                Activity.user == user,
            )
        )
    ):
        activity = await create_activity(
            session, activity_type, target.id, user
        )

    return activity
