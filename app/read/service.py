from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Manga, Novel, User, Read
from app.service import create_log
from sqlalchemy import select
from .schemas import ReadArgs
from app.utils import utcnow
from app import constants


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
