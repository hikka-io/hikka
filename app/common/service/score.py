from app.models import AnimeWatch, MangaRead, NovelRead, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import constants
from uuid import UUID


async def get_user_list_score(
    session: AsyncSession, content_type: str, content_id: UUID, user: User
):
    model = {
        constants.CONTENT_ANIME: AnimeWatch,
        constants.CONTENT_MANGA: MangaRead,
        constants.CONTENT_NOVEL: NovelRead,
    }.get(content_type)

    query = select(model).filter(model.user_id == user.id)

    if content_type == constants.CONTENT_ANIME:
        query = query.filter(model.anime_id == content_id)

    if content_type == constants.CONTENT_MANGA:
        query = query.filter(model.manga_id == content_id)

    if content_type == constants.CONTENT_NOVEL:
        query = query.filter(model.novel_id == content_id)

    if record := await session.scalar(query):
        return record.score

    return 0
