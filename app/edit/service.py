from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import EditArgs, ContentTypeEnum
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload
from datetime import datetime
from app import constants

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

# This is hack-ish way to have single function for different types of content
# As long as it does the job we can keep it (why not)
content_type_to_class = {
    constants.CONTENT_STAFF: AnimeStaffRole,
    constants.CONTENT_CHARACTER: Character,
    constants.CONTENT_GENRE: AnimeGenre,
    constants.CONTENT_COMPANY: Company,
    constants.CONTENT_PERSON: Person,
    constants.CONTENT_ANIME: Anime,
}


async def get_edit(session: AsyncSession, edit_id: int) -> ContentEdit | None:
    """Return ContentEdit by edit_id"""

    return await session.scalar(
        select(ContentEdit)
        .filter(ContentEdit.edit_id == edit_id)
        .options(
            selectinload(ContentEdit.moderator),
            selectinload(ContentEdit.author),
        )
    )


async def get_content_by_id(
    session: AsyncSession, content_type: ContentTypeEnum, content_id: str
) -> AnimeStaffRole | AnimeGenre | Character | Company | Person | Anime | None:
    """Return editable content by content_type and content_id"""

    content_model = content_type_to_class[content_type]
    return await session.scalar(
        select(content_model).filter(content_model.id == content_id)
    )


# ToDo: figure out what to do with anime episodes that do not have a slug
async def get_content_by_slug(
    session: AsyncSession, content_type: ContentTypeEnum, slug: str
) -> AnimeStaffRole | AnimeGenre | Character | Company | Person | Anime | None:
    """Return editable content by content_type and slug"""

    content_model = content_type_to_class[content_type]
    return await session.scalar(
        select(content_model).filter(content_model.slug == slug)
    )


async def count_edits(session: AsyncSession, content_id: str) -> int:
    """Count edits for give content"""

    return await session.scalar(
        select(func.count(ContentEdit.id)).filter(
            ContentEdit.content_id == content_id
        )
    )


async def get_edits(
    session: AsyncSession,
    content_id: str,
    limit: int,
    offset: int,
) -> list[ContentEdit]:
    """Return edits for give content"""

    return await session.scalars(
        select(ContentEdit)
        .filter(ContentEdit.content_id == content_id)
        .options(
            selectinload(ContentEdit.moderator),
            selectinload(ContentEdit.author),
        )
        .order_by(desc(ContentEdit.edit_id))
        .limit(limit)
        .offset(offset)
    )


async def create_pending_edit(
    session: AsyncSession,
    content_type: ContentTypeEnum,
    content_id: str,
    args: EditArgs,
    author: User,
) -> ContentEdit:
    """Create edit for given content_id with pending status"""

    # ToDo: this function looks atrocious -> refactor it

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
            "content_type": content_type,
            "description": description,
            "content_id": content_id,
            "author": author,
            "created": now,
            "updated": now,
            "after": after,
        }
    )

    session.add(edit)
    await session.commit()

    return edit


async def approve_pending_edit(
    session: AsyncSession,
    edit: ContentEdit,
    moderator: User,
) -> ContentEdit:
    """Approve edit for given content_id"""

    content = await get_content_by_id(
        session, edit.content_type, edit.content_id
    )

    before = {}

    for key, value in edit.after.items():
        before[key] = getattr(content, key)
        setattr(content, key, value)

    edit.status = constants.EDIT_APPROVED
    edit.updated = datetime.now()
    edit.moderator = moderator
    edit.before = before

    session.add(edit)
    session.add(content)
    await session.commit()

    return edit


async def deny_pending_edit(
    session: AsyncSession,
    edit: ContentEdit,
    moderator: User,
) -> ContentEdit:
    """Deny edit for given content_id"""

    edit.status = constants.EDIT_DENIED
    edit.updated = datetime.now()
    edit.moderator = moderator

    session.add(edit)
    await session.commit()

    return edit
