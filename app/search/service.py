from app.models import Anime, AnimeGenre, Company
from .schemas import AnimeSearchArgs
from . import utils


async def company_count(slugs):
    return await Company.filter(slug__in=slugs).count()


async def anime_genre_count(slugs):
    return await AnimeGenre.filter(slug__in=slugs).count()


async def anime_search_query(search: AnimeSearchArgs):
    query = Anime.filter()

    if len(search.rating) > 0:
        query = query.filter(rating__in=utils.enum_list_values(search.rating))

    if len(search.status) > 0:
        query = query.filter(status__in=utils.enum_list_values(search.status))

    if len(search.source) > 0:
        query = query.filter(source__in=utils.enum_list_values(search.source))

    if len(search.media_type) > 0:
        query = query.filter(
            media_type__in=utils.enum_list_values(search.media_type)
        )

    if len(search.producers) > 0:
        producers = await Company.filter(slug__in=search.producers)
        query = query.filter(producers__in=producers)

    if len(search.studios) > 0:
        studios = await Company.filter(slug__in=search.studios)
        query = query.filter(studios__in=studios)

    if len(search.genres) > 0:
        genres = await AnimeGenre.filter(slug__in=search.genres)
        query = query.filter(genres__in=genres)

    # years
    # season

    query = query.order_by(*utils.build_order_by(search.sort))

    return query
