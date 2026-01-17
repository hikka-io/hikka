from sqlalchemy import select, update, func
from app.database import sessionmanager
from app import constants

from app.models import (
    AnimeWatch,
    MangaRead,
    NovelRead,
    Anime,
    Manga,
    Novel,
)


async def update_scores():
    async with sessionmanager.session() as session:
        for entry in [
            (constants.CONTENT_ANIME, Anime, AnimeWatch),
            (constants.CONTENT_MANGA, Manga, MangaRead),
            (constants.CONTENT_NOVEL, Novel, NovelRead),
        ]:
            content_type, content_model, list_model = entry

            if content_type == constants.CONTENT_ANIME:
                content_id = list_model.anime_id.label("content_id")
            else:
                content_id = list_model.content_id.label("content_id")

            subquery = (
                select(
                    content_id,
                    func.round(func.avg(list_model.score), 2).label("score"),
                    func.count(list_model.id).label("scored_by"),
                )
                .filter(list_model.score > 0)
                .group_by(content_id)
                .subquery()
            )

            await session.execute(
                update(content_model)
                .values(
                    native_score=subquery.c.score,
                    native_scored_by=subquery.c.scored_by,
                )
                .filter(content_model.id == subquery.c.content_id)
            )

            await session.commit()

            scored_count = await session.scalar(
                select(func.count(content_model.id)).filter(
                    content_model.native_scored_by > 0,
                    content_model.native_score > 0,
                )
            )

            print(
                f"Calculated native score for {scored_count} {content_type} records"
            )
