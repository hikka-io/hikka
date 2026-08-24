from app.models import Moderation, Edit, Comment, Collection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, desc
from uuid import UUID


async def get_moderation(
    session: AsyncSession,
    user_id: UUID,
    log_id: UUID,
    target_type: str | None = None,
):
    query = (
        select(Moderation)
        .options(joinedload(Moderation.user))
        .filter(
            Moderation.user_id == user_id,
            Moderation.log_id == log_id,
        )
    )

    if target_type:
        query = query.filter(
            Moderation.target_type == target_type,
        )

    return await session.scalar(query.order_by(desc(Moderation.created)))


async def get_edit(session: AsyncSession, content_id: UUID):
    return await session.scalar(
        select(Edit)
        .options(joinedload(Edit.author))
        .filter(Edit.id == content_id)
    )


async def get_comment(session: AsyncSession, content_id: UUID):
    return await session.scalar(
        select(Comment)
        .options(joinedload(Comment.author))
        .filter(Comment.id == content_id)
    )


async def get_collection(session: AsyncSession, content_id: UUID):
    return await session.scalar(
        select(Collection)
        .options(joinedload(Collection.author))
        .filter(Collection.id == content_id)
    )
