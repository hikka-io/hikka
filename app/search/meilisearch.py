from meilisearch_python_async.errors import MeilisearchError
from meilisearch_python_async import Client
from app.utils import pagination_dict
from .schemas import AnimeSearchArgs
from app.errors import Abort
from app import constants
import config


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


async def anime_search(search: AnimeSearchArgs):
    try:
        async with Client(**config.meilisearch) as client:
            index = client.index(constants.ANIME_SEARCH_INDEX)

            result = await index.search(
                hits_per_page=constants.SEARCH_RESULT_LIMIT,
                filter=build_anime_filters(search),
                query=search.query,
                page=search.page,
                sort=search.sort,
            )

            return {
                "pagination": pagination_dict(
                    result.total_hits, result.page, result.hits_per_page
                ),
                "list": result.hits,
            }

    except MeilisearchError:
        raise Abort("search", "query-down")
