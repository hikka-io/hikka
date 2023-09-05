from app.models import User, Anime, ContentEdit
from sqlalchemy.ext.asyncio import AsyncSession
from app.service import get_anime_by_id
from datetime import datetime
from sqlalchemy import select
from app import constants
from typing import Union


from .schemas import (
    AnimeEditArgs,
)


async def get_edit_by_id(
    session: AsyncSession, edit_id: int
) -> Union[ContentEdit, None]:
    return await session.scalar(select(ContentEdit).filter_by(edit_id=edit_id))


async def create_anime_edit_request(
    args: AnimeEditArgs,
    user: User,
    anime: Anime,
    session: AsyncSession,
) -> ContentEdit:
    # Pretty much the only reason we convert it to dict here is so that we can
    # get rid of non-edit fields like "description" in a neat way
    args = args.dict()
    description = args.pop("description")

    after = {}

    for key, value in args.items():
        if not value:
            continue

        after[key] = value

    now = datetime.utcnow()

    edit = ContentEdit(
        **{
            "status": constants.EDIT_PENDING,
            "content_id": anime.id,
            "content_type": constants.CONTENT_ANIME,
            "after": after,
            "created": now,
            "updated": now,
            "author": user,
            "description": description,
        }
    )

    session.add(edit)
    await session.commit()

    return edit


async def approve_anime_edit_request(
    user: User,
    edit: ContentEdit,
    session: AsyncSession,
) -> ContentEdit:
    anime = await get_anime_by_id(session, edit.content_id)
    before = {}

    for key, value in edit.after.items():
        before[key] = getattr(anime, key)
        setattr(anime, key, value)

    edit.status = constants.EDIT_APPROVED
    edit.before = before
    edit.updated = datetime.now()
    edit.moderator = user

    session.add(edit)
    session.add(anime)
    await session.commit()

    return edit


async def deny_anime_edit_request(
    user: User,
    edit: ContentEdit,
    session: AsyncSession,
) -> ContentEdit:
    edit.status = constants.EDIT_DENIED
    edit.updated = datetime.now()
    edit.moderator = user

    session.add(edit)
    await session.commit()

    return edit
