from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.orm import subqueryload
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


def get_franchise_relations(franchise: Franchise):
    slugs = {
        (content.data_type, content.content_id): content.slug
        for content in franchise.anime + franchise.manga + franchise.novel
    }

    relations = []

    for relation in franchise.relations:
        source = (relation["content_type"], relation["content_id"])
        target = (
            relation["related_content_type"],
            relation["related_content_id"],
        )

        # Skip relations to deleted content or content we don't have
        if source not in slugs or target not in slugs:
            continue

        relations.append(
            {
                "related_content_type": relation["related_content_type"],
                "relation_type": relation["relation_type"],
                "content_type": relation["content_type"],
                "related_slug": slugs[target],
                "slug": slugs[source],
            }
        )

    return relations


async def get_franchise(
    session: AsyncSession,
    content: Anime | Manga | Novel,
    request_user: User | None,
):
    franchise = await session.scalar(
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
        .options(
            with_loader_criteria(Anime, Anime.deleted == False),  # noqa: E712
            with_loader_criteria(Manga, Manga.deleted == False),  # noqa: E712
            with_loader_criteria(Novel, Novel.deleted == False),  # noqa: E712
        )
    )

    return {
        "relations": get_franchise_relations(franchise),
        "anime": franchise.anime,
        "manga": franchise.manga,
        "novel": franchise.novel,
    }
