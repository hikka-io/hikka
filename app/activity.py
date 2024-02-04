from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from app import constants
from uuid import UUID

from app.models import (
    AnimeFavourite,
    Activity,
    User,
)


async def favourite_anime_add(
    session: AsyncSession,
    action: str,
    user: User,
    target_id: UUID,
    data: dict,
):
    # threshold = datetime.utcnow()
    # if activity := await session.scalar(
    #     select(Activity).filter(
    #         Activity.activity_type == activity_type,
    #         Activity.target_id == target_id,
    #         Activity.user == user,
    #     )
    # ):
    #     pass

    # now = datetime.utcnow()
    # activity = Activity(
    #     **{
    #         "target_id": target_id,
    #         "activity_type": "favourite_anime",
    #         "updated": now,
    #         "created": now,
    #         "user": user,
    #         "data": data,
    #     }
    # )

    # session.add(activity)
    # await session.commit()

    print(activity.activity_type)

    return activity


async def handle_activity(
    session: AsyncSession,
    action: str,
    user: User,
    target: None | AnimeFavourite = None,
    data: dict = {},
) -> Activity | None:
    """This function creates Activity record for user action"""

    target_id = target.id if target else None

    if action == constants.ACTIVITY_FAVOURITE_ANIME_ADD:
        return await favourite_anime_add(
            session,
            action,
            user,
            target_id,
            data,
        )

    return None
