from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import EditArgs, ContentTypeEnum
from sqlalchemy import select, desc, func
from datetime import datetime
from app import constants

from app.models import (
    PersonContentEdit,
    AnimeContentEdit,
    ContentEdit,
    Person,
    Anime,
    User,
)

# This is hack-ish way to have single function for different types of content
# As long as it does the job we can keep it (why not)
content_type_to_content_class = {
    constants.CONTENT_PERSON: Person,
    constants.CONTENT_ANIME: Anime,
}

content_type_to_edit_class = {
    constants.CONTENT_PERSON: PersonContentEdit,
    constants.CONTENT_ANIME: AnimeContentEdit,
}


async def get_edit(session: AsyncSession, edit_id: int) -> ContentEdit | None:
    """Return ContentEdit by edit_id"""

    return await session.scalar(
        select(ContentEdit).filter(ContentEdit.edit_id == edit_id)
    )


# ToDo: figure out what to do with anime episodes that do not have a slug
async def get_content_by_slug(
    session: AsyncSession, content_type: ContentTypeEnum, slug: str
) -> Person | Anime | None:
    """Return editable content by content_type and slug"""

    content_model = content_type_to_content_class[content_type]
    return await session.scalar(
        select(content_model).filter(content_model.slug == slug)
    )


async def count_edits_by_content_id(
    session: AsyncSession, content_id: str
) -> int:
    """Count edits for given content"""

    return await session.scalar(
        select(func.count(ContentEdit.id)).filter(
            ContentEdit.content_id == content_id
        )
    )


async def get_edits_by_content_id(
    session: AsyncSession,
    content_id: str,
    limit: int,
    offset: int,
) -> list[ContentEdit]:
    """Return edits for given content"""

    return await session.scalars(
        select(ContentEdit)
        .filter(ContentEdit.content_id == content_id)
        .order_by(desc(ContentEdit.edit_id))
        .limit(limit)
        .offset(offset)
    )


async def count_edits(session: AsyncSession) -> int:
    """Count all edits"""

    return await session.scalar(select(func.count(ContentEdit.id)))


async def get_edits(
    session: AsyncSession,
    limit: int,
    offset: int,
) -> list[ContentEdit]:
    """Return all edits"""

    return await session.scalars(
        select(ContentEdit)
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
) -> AnimeContentEdit:
    """Create edit for given content_id with pending status"""

    edit_model = content_type_to_edit_class[content_type]

    now = datetime.utcnow()

    edit = edit_model(
        **{
            "status": constants.EDIT_PENDING,
            "description": args.description,
            "content_type": content_type,
            "content_id": content_id,
            "after": args.after,
            "author": author,
            "created": now,
            "updated": now,
        }
    )

    session.add(edit)
    await session.commit()

    # This step is needed to load content relation for slug
    await session.refresh(edit)

    return edit


async def update_pending_edit(
    session: AsyncSession,
    edit: ContentEdit,
    args: EditArgs,
) -> ContentEdit:
    """Update pending edit"""

    edit.updated = datetime.now()
    edit.description = args.description
    edit.after = args.after

    session.add(edit)
    await session.commit()

    return edit


async def close_pending_edit(
    session: AsyncSession,
    edit: ContentEdit,
) -> ContentEdit:
    """Close pending edit"""

    edit.status = constants.EDIT_CLOSED
    edit.updated = datetime.now()

    session.add(edit)
    await session.commit()

    return edit


async def accept_pending_edit(
    session: AsyncSession,
    edit: ContentEdit,
    moderator: User,
) -> ContentEdit:
    """Accept pending edit"""

    content = edit.content

    before = {}

    for key, value in edit.after.items():
        before[key] = getattr(content, key)
        setattr(content, key, value)

    edit.status = constants.EDIT_ACCEPTED
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
    """Deny pending edit"""

    edit.status = constants.EDIT_DENIED
    edit.updated = datetime.now()
    edit.moderator = moderator

    session.add(edit)
    await session.commit()

    return edit
