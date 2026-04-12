from app.models import AnimeWatch, Anime, Manga, Novel, Read
from sqlalchemy.sql.expression import nulls_last
from sqlalchemy import desc, asc

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


def build_manga_order_by(sort: list[str]):
    return build_order_by(
        sort,
        order_mapping=read_order_mapping
        | {
            "native_scored_by": Manga.native_scored_by,
            "native_score": Manga.native_score,
            "media_type": Manga.media_type,
            "start_date": Manga.start_date,
            "scored_by": Manga.scored_by,
            "created": Manga.created,
            "updated": Manga.updated,
            "score": Manga.score,
        },
        tiebreaker=desc(Manga.content_id),
        nullable=["start_date"],
    )


def build_novel_order_by(sort: list[str]):
    return build_order_by(
        sort,
        order_mapping=read_order_mapping
        | {
            "native_scored_by": Novel.native_scored_by,
            "native_score": Novel.native_score,
            "media_type": Novel.media_type,
            "start_date": Novel.start_date,
            "scored_by": Novel.scored_by,
            "created": Novel.created,
            "updated": Novel.updated,
            "score": Novel.score,
        },
        tiebreaker=desc(Novel.content_id),
        nullable=["start_date"],
    )
