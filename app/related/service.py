from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.orm import subqueryload
from sqlalchemy.orm import joinedload
from sqlalchemy import select

from app.models import (
    AnimeWatch,
    MangaRead,
    NovelRead,
    Franchise,
    Anime,
    Manga,
    Novel,
    User,
)


async def get_franchise(
    session: AsyncSession,
    content: Anime | Manga | Novel,
    request_user: User | None,
):
    return await session.scalar(
        select(Franchise)
        .filter(Franchise.id == content.franchise_id)
        .options(
            subqueryload(Franchise.anime).joinedload(Anime.watch),
            with_loader_criteria(
                AnimeWatch,
                AnimeWatch.user_id == request_user.id if request_user else None,
            ),
        )
        .options(
            subqueryload(Franchise.manga).joinedload(Manga.read),
            with_loader_criteria(
                MangaRead,
                MangaRead.user_id == request_user.id if request_user else None,
            ),
        )
        .options(
            subqueryload(Franchise.novel).joinedload(Novel.read),
            with_loader_criteria(
                NovelRead,
                NovelRead.user_id == request_user.id if request_user else None,
            ),
        )
    )
