from app.models import Company, AnimeGenre
from .schemas import AnimeSearchArgs
from app.errors import Abort


async def validate_search_anime(search: AnimeSearchArgs):
    # Check if provided producers exist
    if len(search.producers) > 0:
        producers = await Company.filter(slug__in=search.producers).count()
        if producers != len(search.producers):
            raise Abort("search", "unknown-producer")

    # Check if provided studios exist
    if len(search.studios) > 0:
        studios = await Company.filter(slug__in=search.studios).count()
        if studios != len(search.studios):
            raise Abort("search", "unknown-studio")

    # Check if provided genres exist
    if len(search.genres) > 0:
        genres = await AnimeGenre.filter(slug__in=search.genres).count()
        if genres != len(search.genres):
            raise Abort("search", "unknown-genre")

    return search
