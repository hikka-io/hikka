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

# Native scores are calculated as a Bayesian weighted score
#
# Weighted score = (v / (v + m)) * S + (m / (v + m)) * C
#
# S = Average score for the anime/manga/novel
# v = Number of users who set score in list for anime/manga/novel
# m = Minimum number of scored users required to calculate a score
# C = The mean score across the entire database for that content type
#
# Native score for titles with number of scoress less than
# m will be set to zero
#
# TODO: in future we would need to filter out v similar to MAL
# to prevent score manipulation


MINIMUM_SCORED_USERS = 10  # aka m


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

            # Mean score for content type (C)
            global_mean = await session.scalar(
                select(func.avg(list_model.score)).filter(list_model.score > 0)
            )

            if global_mean is None:
                print(f"No scores found for {content_type}, skipping")
                continue

            m = MINIMUM_SCORED_USERS
            c = float(global_mean)

            # Raw average (S) score and vote count (v)
            subquery = (
                select(
                    content_id,
                    func.avg(list_model.score).label("raw_score"),
                    func.count(list_model.id).label("scored_by"),
                )
                .filter(list_model.score > 0)
                .group_by(content_id)
                .subquery()
            )

            v = subquery.c.scored_by
            s = subquery.c.raw_score

            # Final weighted score
            weighted_score = func.round(
                (v / (v + m)) * s + (m / (v + m)) * c, 2
            )

            await session.execute(
                update(content_model)
                .values(
                    native_score=weighted_score,
                    native_scored_by=subquery.c.scored_by,
                )
                .filter(content_model.id == subquery.c.content_id)
            )

            # Set native score to zero for titles with less than m votes
            await session.execute(
                update(content_model)
                .values(native_score=0)
                .filter(content_model.native_scored_by < m)
            )

            await session.commit()

            scored_count = await session.scalar(
                select(func.count(content_model.id)).filter(
                    content_model.native_scored_by > 0,
                    content_model.native_score > 0,
                )
            )

            print(
                f"Calculated weighted score for {scored_count}"
                f" {content_type} records (C={round(c, 2)}, m={m})"
            )
