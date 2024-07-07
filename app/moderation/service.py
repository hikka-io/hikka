from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select
from sqlalchemy import asc, select, desc, func

from app.models import (
    Moderation,
    User,
)
from app.service import get_user_by_username
from .schemas import ModerationSearchArgs


async def moderation_search_filter(
    session: AsyncSession,
    args: ModerationSearchArgs,
    query: Select,
):
    if args.author:
        author = await get_user_by_username(session, args.author)
        query = query.filter(Moderation.user == author)

    if args.target_type:
        query = query.filter(Moderation.target_type == args.target_type)

    return query


def build_moderation_order_by(sort: str):
    order_mapping = {
        "created": Moderation.created,
    }

    field, order = sort.split(":")

    order_by = (
        desc(order_mapping[field])
        if order == "desc"
        else asc(order_mapping[field])
    )

    return order_by


async def get_moderation_count(
    session: AsyncSession, args: ModerationSearchArgs
) -> int:
    query = await moderation_search_filter(
        session, args, select(func.count(Moderation.id))
    )

    return await session.scalar(query)


async def get_moderation(
    session: AsyncSession, args: ModerationSearchArgs, limit: int, offset: int
) -> list[Moderation]:
    """Get moderation log"""

    query = await moderation_search_filter(session, args, select(Moderation))

    query = query.order_by(build_moderation_order_by(args.sort))
    query = query.limit(limit).offset(offset)

    return await session.scalars(query)
