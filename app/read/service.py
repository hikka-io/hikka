from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager
from sqlalchemy import select, desc, func
from app.service import create_log
from .schemas import ReadArgs
from app.utils import utcnow
from app import constants

from app.models import (
    Follow,
    Manga,
    Novel,
    User,
    Read,
)


async def get_read(
    session: AsyncSession,
    content_type: str,
    content: Manga | Novel,
    user: User,
):
    return await session.scalar(
        select(Read).filter(
            Read.deleted == False,  # noqa: E712
            Read.content_type == content_type,
            Read.content_id == content.id,
            Read.user == user,
        )
    )


async def save_read(
    session: AsyncSession,
    content_type: str,
    content: Manga | Novel,
    user: User,
    args: ReadArgs,
):
    now = utcnow()
    log_type = constants.LOG_READ_UPDATE

    # Create read record if missing
    if not (read := await get_read(session, content_type, content, user)):
        log_type = constants.LOG_READ_CREATE
        read = Read()
        read.created = now
        read.content_type = content_type
        read.content_id = content.id
        read.user = user

    log_before = {}
    log_after = {}

    # Set attributes from args to read record
    for key, new_value in args.model_dump().items():
        # Here we add changes to log's before/after dicts only if there are changes
        old_value = getattr(read, key)
        if old_value != new_value:
            log_before[key] = old_value
            setattr(read, key, new_value)
            log_after[key] = new_value

    # Update updated field
    read.updated = now

    # Update user last list update
    user.updated = now
    session.add_all([read, user])

    await session.commit()

    if log_before != {} and log_after != {} and log_before != log_after:
        await create_log(
            session,
            log_type,
            user,
            content.id,
            {
                "content_type": content_type,
                "before": log_before,
                "after": log_after,
            },
        )

    return read


async def delete_read(
    session: AsyncSession,
    read: Read,
    user: User,
):
    await session.delete(read)

    # Update user last list update
    user.updated = utcnow()
    session.add(user)

    await create_log(
        session,
        constants.LOG_READ_DELETE,
        user,
        read.content.id,
    )

    await session.commit()


async def get_manga_read_following_total(
    session: AsyncSession,
    user: User,
    content_type: str,
    content: Manga | Novel,
):
    return await session.scalar(
        select(func.count(User.id))
        .join(Follow, Follow.followed_user_id == User.id)
        .filter(Follow.user_id == user.id)
        .join(User.read)
        .filter(Read.content_type == content_type)
        .filter(Read.content_id == content.id)
    )


async def get_manga_read_following(
    session: AsyncSession,
    user: User,
    content_type: str,
    content: Manga | Novel,
    limit: int,
    offset: int,
):
    return await session.scalars(
        select(User)
        .join(Follow, Follow.followed_user_id == User.id)
        .filter(Follow.user_id == user.id)
        .join(User.read)
        .filter(Read.content_type == content_type)
        .filter(Read.content_id == content.id)
        .options(contains_eager(User.read))
        .order_by(desc(Read.score), desc(Read.updated))
        .limit(limit)
        .offset(offset)
    )
