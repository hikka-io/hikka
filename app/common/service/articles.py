from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict
from sqlalchemy import select
from app import constants

from app.models import (
    Article,
    Anime,
    Manga,
    Novel,
)


# WFT is this?
# TODO: rework and remove this function
async def load_articles_content(
    session: AsyncSession,
    article_or_articles: Article | list[Article],
):
    if isinstance(article_or_articles, Article):
        articles = [article_or_articles]
        single_input = True
    else:
        articles = article_or_articles
        single_input = False

    # No articles so why bother
    if not articles:
        return article_or_articles

    references = defaultdict(set)

    for article in articles:
        if article.content_type and article.content_id:
            references[article.content_type].add(article.content_id)

    anime_dict, manga_dict, novel_dict = {}, {}, {}

    if constants.CONTENT_ANIME in references:
        anime = await session.scalars(
            select(Anime).filter(
                Anime.id.in_(list(references[constants.CONTENT_ANIME]))
            )
        )

        anime_dict = {entry.id: entry for entry in anime.all()}

    if constants.CONTENT_MANGA in references:
        manga = await session.scalars(
            select(Manga).filter(
                Manga.id.in_(list(references[constants.CONTENT_MANGA]))
            )
        )

        manga_dict = {entry.id: entry for entry in manga.all()}

    if constants.CONTENT_NOVEL in references:
        novel = await session.scalars(
            select(Novel).filter(
                Novel.id.in_(list(references[constants.CONTENT_NOVEL]))
            )
        )

        novel_dict = {entry.id: entry for entry in novel.all()}

    for article in articles:
        match article.content_type:
            case constants.CONTENT_ANIME:
                article.content = anime_dict.get(article.content_id)

            case constants.CONTENT_MANGA:
                article.content = manga_dict.get(article.content_id)

            case constants.CONTENT_NOVEL:
                article.content = novel_dict.get(article.content_id)

            case _:
                article.content = None

    return articles[0] if single_input else articles
