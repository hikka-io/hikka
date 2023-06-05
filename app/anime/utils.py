from .schemas import AnimeSearchArgs
from sqlalchemy import desc, asc


def build_anime_filters(search: AnimeSearchArgs):
    rating = [f"rating = {rating}" for rating in search.rating]

    status = [f"status = {status}" for status in search.status]

    source = [f"source = {source}" for source in search.source]

    season = [f"season = {season}" for season in search.season]

    producers = [f"producers = {producer}" for producer in search.producers]
    studios = [f"studios = {studio}" for studio in search.studios]
    genres = [f"genres = {genre}" for genre in search.genres]

    year = []

    if search.years[0]:
        year.append([f"year>={search.years[0]}"])

    if search.years[1]:
        year.append([f"year<={search.years[1]}"])

    return [
        rating,
        status,
        source,
        season,
        producers,
        studios,
        *genres,
        *year,
    ]


def build_order_by(sort: list[str]):
    return [
        desc(field) if order == "desc" else asc(field)
        for field, order in (entry.split(":") for entry in sort)
    ] + [desc("content_id")]
