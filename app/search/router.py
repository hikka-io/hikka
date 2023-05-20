from app.utils import pagination_dict, pagination
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import validate_search_anime
from fastapi import APIRouter, Depends
from .schemas import AnimeSearchArgs
from app.database import get_session
from . import meilisearch
from typing import Tuple
from . import service


router = APIRouter(prefix="/search")


@router.post("/anime")
async def search_anime(
    session: AsyncSession = Depends(get_session),
    search: AnimeSearchArgs = Depends(validate_search_anime),
):
    # if not search.query:
    #     total = await service.anime_search_total(session, search)
    #     limit, offset = pagination(search.page, limit=12)
    #     result = await service.anime_search(session, search, limit, offset)

    #     return {
    #         "pagination": pagination_dict(total, search.page, limit),
    #         "list": [anime for anime in result],
    #     }

    return await meilisearch.anime_search(search)
