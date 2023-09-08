from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import EditArgs, ContentTypeEnum
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload
from datetime import datetime
from app import constants
from typing import Union

from app.models import (
    AnimeStaffRole,
    ContentEdit,
    AnimeGenre,
    Character,
    Company,
    Person,
    Anime,
    User,
)

content_type_to_class = {
    constants.CONTENT_ANIME: Anime,
    # constants.CONTENT_MANGA: ,
    constants.CONTENT_CHARACTER: Character,
    constants.CONTENT_COMPANY: Company,
    # constants.CONTENT_EPISODE: AnimeEpisode,
    constants.CONTENT_GENRE: AnimeGenre,
    constants.CONTENT_PERSON: Person,
    constants.CONTENT_STAFF: AnimeStaffRole,
}


async def get_content_by_id(
    session: AsyncSession, content_type: ContentTypeEnum, content_id: str
) -> Union[Anime, Character, Company, AnimeGenre, Person, AnimeStaffRole, None]:
    return await session.scalar(
        select(content_type_to_class[content_type]).filter_by(id=content_id)
    )


# Todo: figure out what to do with anime episodes that do not have a slug
async def get_content_by_slug(
    session: AsyncSession, content_type: ContentTypeEnum, slug: str
) -> Union[Anime, Character, Company, AnimeGenre, Person, AnimeStaffRole, None]:
    return await session.scalar(
        select(content_type_to_class[content_type]).filter_by(slug=slug)
    )


async def get_edit_by_id(
    session: AsyncSession, edit_id: int
) -> Union[ContentEdit, None]:
    return await session.scalar(
        select(ContentEdit)
        .filter_by(edit_id=edit_id)
        .options(
            selectinload(ContentEdit.author),
            selectinload(ContentEdit.moderator),
        )
    )


async def count_edits_by_content_id(
    session: AsyncSession,
    content_id: str,
) -> int:
    return await session.scalar(
        select(func.count(ContentEdit.id)).filter_by(content_id=content_id)
    )


async def get_edits_by_content_id(
    session: AsyncSession,
    content_id: str,
    limit: int,
    offset: int,
):
    return await session.scalars(
        select(ContentEdit)
        .filter_by(content_id=content_id)
        .options(
            selectinload(ContentEdit.author),
            selectinload(ContentEdit.moderator),
        )
        .order_by(desc("edit_id"))
        .limit(limit)
        .offset(offset)
    )


async def create_edit_request(
    args: EditArgs,
    content_id: str,
    content_type: ContentTypeEnum,
    user: User,
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
            "content_id": content_id,
            "content_type": content_type,
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


async def approve_edit_request(
    user: User,
    edit: ContentEdit,
    session: AsyncSession,
) -> ContentEdit:
    content = await get_content_by_id(
        session, edit.content_type, edit.content_id
    )
    before = {}

    for key, value in edit.after.items():
        before[key] = getattr(content, key)
        setattr(content, key, value)

    edit.status = constants.EDIT_APPROVED
    edit.before = before
    edit.updated = datetime.now()
    edit.moderator = user

    session.add(edit)
    session.add(content)
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
