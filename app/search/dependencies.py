from .schemas import AnimeSearchArgs
from app.errors import Abort
from . import service


async def validate_search_anime(search: AnimeSearchArgs):
    # Check if provided producers exist
    if len(search.producers) > 0:
        producers = await service.company_count(search.producers)
        if producers != len(search.producers):
            raise Abort("search", "unknown-producer")

    # Check if provided studios exist
    if len(search.studios) > 0:
        studios = await service.company_count(search.studios)
        if studios != len(search.studios):
            raise Abort("search", "unknown-studio")

    # Check if provided genres exist
    if len(search.genres) > 0:
        genres = await service.anime_genre_count(search.genres)
        if genres != len(search.genres):
            raise Abort("search", "unknown-genre")

    return search
