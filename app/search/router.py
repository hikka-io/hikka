from app.utils import pagination_dict, pagination
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import validate_search_anime
from fastapi import APIRouter, Depends
from .schemas import AnimeSearchArgs
from app.database import get_session
from typing import Tuple
from . import service


router = APIRouter(prefix="/search")


@router.post("/anime")
async def search_anime(
    params: Tuple[AnimeSearchArgs, list, list, list] = Depends(
        validate_search_anime
    ),
    session: AsyncSession = Depends(get_session),
):
    total = await service.anime_search_total(session, *params)
    limit, offset = pagination(params[0].page)
    result = await service.anime_search(session, limit, offset, *params)

    return {
        "pagination": pagination_dict(total, params[0].page, limit),
        "list": [anime for anime in result],
    }

    # return {"query": str(search_query)}
    # return {"total": total}
    # if not search.query:
    #     search_query = await service.anime_search_query(search)

    #     total = await search_query.count()
    #     limit, offset, size = pagination(search.page, size=12)

    #     anime_list = (
    #         await search_query.prefetch_related("genres")
    #         .limit(limit)
    #         .offset(offset)
    #     )

    #     result = [
    #         {
    #             "media_type": anime.media_type,
    #             "scored_by": anime.scored_by,
    #             "title_ua": anime.title_ua,
    #             "title_en": anime.title_en,
    #             "title_ja": anime.title_ja,
    #             "score": anime.score,
    #             "slug": anime.slug,
    #             "genres": [genre.slug for genre in anime.genres],
    #         }
    #         for anime in anime_list
    #     ]

    #     return {
    #         "pagination": pagination_dict(total, search.page, size),
    #         "list": result,
    #     }

    # return {"query": search.query}
