from app.service import content_type_to_content_class
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import ReadArgs, ReadSearchArgs
from sqlalchemy.orm import contains_eager
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from app.utils import utcnow
from app import constants
import random

from app.service import (
    build_manga_order_by,
    build_novel_order_by,
    manga_search_filter,
    novel_search_filter,
    create_log,
)

from app.models import (
    MangaRead,
    NovelRead,
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
        select(Read)
        .filter(
            Read.deleted == False,  # noqa: E712
            Read.content_type == content_type,
            Read.content_id == content.id,
            Read.user == user,
        )
        .options(
            joinedload(MangaRead.content),
            joinedload(NovelRead.content),
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

    # We need to do this in order to return object with content inside
    # when read record is created for the first time
    read_model = {
        constants.CONTENT_MANGA: MangaRead,
        constants.CONTENT_NOVEL: NovelRead,
    }.get(content_type)

    # Create read record if missing
    if not (read := await get_read(session, content_type, content, user)):
        log_type = constants.LOG_READ_CREATE
        read = read_model()
        read.content = content
        read.created = now
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


async def get_read_following_total(
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


async def get_read_following(
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


async def get_user_read_stats(
    session: AsyncSession,
    user: User,
    content_type: str,
    status: str,
):
    return await session.scalar(
        select(func.count(Read.id)).filter(
            Read.content_type == content_type,
            Read.deleted == False,  # noqa: E712
            Read.status == status,
            Read.user == user,
        )
    )


async def random_read(
    session: AsyncSession,
    user: User,
    content_type: str,
    status: str,
):
    content_model = content_type_to_content_class[content_type]

    content_ids = await session.scalars(
        select(Read.content_id).filter(
            Read.content_type == content_type,
            Read.status == status,
            Read.user == user,
        )
    )

    return await session.scalar(
        select(content_model).filter(
            content_model.id == random.choice(content_ids.all())
        )
    )


async def get_user_read_list_count(
    session: AsyncSession,
    search: ReadSearchArgs,
    content_type: str,
    user: User,
) -> int:
    query = select(func.count(Read.id)).filter(
        Read.content_type == content_type,
        Read.deleted == False,  # noqa: E712
        Read.user == user,
    )

    if search.read_status:
        query = query.filter(Read.status == search.read_status)

    if content_type == constants.CONTENT_MANGA:
        query = manga_search_filter(
            search, query.join(MangaRead.content), False
        )

    if content_type == constants.CONTENT_NOVEL:
        query = novel_search_filter(
            search, query.join(NovelRead.content), False
        )

    return await session.scalar(query)


async def get_user_read_list(
    session: AsyncSession,
    search: ReadSearchArgs,
    content_type: str,
    user: User,
    limit: int,
    offset: int,
) -> list[Read]:
    query = select(Read).filter(
        Read.content_type == content_type,
        Read.deleted == False,  # noqa: E712
        Read.user == user,
    )

    if search.read_status:
        query = query.filter(Read.status == search.read_status)

    if content_type == constants.CONTENT_MANGA:
        query = (
            manga_search_filter(
                search,
                query.join(MangaRead.content),
                False,
            )
            .order_by(*build_manga_order_by(search.sort))
            .options(joinedload(MangaRead.content))
        )

    if content_type == constants.CONTENT_NOVEL:
        query = (
            novel_search_filter(
                search,
                query.join(NovelRead.content),
                False,
            )
            .order_by(*build_novel_order_by(search.sort))
            .options(joinedload(NovelRead.content))
        )

    return await session.scalars(query.limit(limit).offset(offset))
