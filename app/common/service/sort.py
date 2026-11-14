from sqlalchemy.sql.expression import nulls_last
from sqlalchemy import desc, asc

from app.models import (
    AnimeWatch,
    Comment,
    Anime,
    Manga,
    Novel,
    Read,
)


read_order_mapping = {
    "read_chapters": Read.chapters,
    "read_volumes": Read.volumes,
    "read_updated": Read.updated,
    "read_created": Read.created,
    "read_score": Read.score,
}


def build_order_by(
    sort: list[str],
    order_mapping,
    tiebreaker=None,
    nullable=[],
):
    order_by = []

    for field, order in (entry.split(":") for entry in sort):
        entry = (
            desc(order_mapping[field])
            if order == "desc"
            else asc(order_mapping[field])
        )

        if field in nullable and order == "desc":
            entry = nulls_last(entry)

        order_by.append(entry)

    if tiebreaker is not None:
        order_by.append(tiebreaker)

    return order_by


def build_anime_order_by(sort: list[str]):
    return build_order_by(
        sort,
        order_mapping={
            "native_scored_by": Anime.native_scored_by,
            "episodes_total": Anime.episodes_total,
            "watch_episodes": AnimeWatch.episodes,
            "watch_updated": AnimeWatch.updated,
            "watch_created": AnimeWatch.created,
            "native_score": Anime.native_score,
            "watch_score": AnimeWatch.score,
            "media_type": Anime.media_type,
            "start_date": Anime.start_date,
            "scored_by": Anime.scored_by,
            "created": Anime.created,
            "updated": Anime.updated,
            "score": Anime.score,
        },
        tiebreaker=desc(Anime.content_id),
        nullable=["start_date"],
    )


def build_read_content_order_by(model: type[Manga | Novel], sort: list[str]):
    return build_order_by(
        sort,
        order_mapping=read_order_mapping
        | {
            "native_scored_by": model.native_scored_by,
            "native_score": model.native_score,
            "media_type": model.media_type,
            "start_date": model.start_date,
            "scored_by": model.scored_by,
            "created": model.created,
            "updated": model.updated,
            "score": model.score,
        },
        tiebreaker=desc(model.content_id),
        nullable=["start_date"],
    )


def build_comments_order_by(sort: list[str]):
    return build_order_by(
        sort,
        order_mapping={
            "total_replies": Comment.total_replies,
            "vote_score": Comment.vote_score,
            "created": Comment.created,
            "updated": Comment.updated,
        },
        tiebreaker=desc(Comment.id),
    )
