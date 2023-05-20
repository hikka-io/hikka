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
    session: AsyncSession = Depends(get_session),
    params: Tuple[AnimeSearchArgs, list, list, list] = Depends(
        validate_search_anime
    ),
):
    search: AnimeSearchArgs = params[0]

    if not search.query:
        total = await service.anime_search_total(session, *params)
        limit, offset = pagination(params[0].page)
        result = await service.anime_search(session, limit, offset, *params)

        return {
            "pagination": pagination_dict(total, search.page, limit),
            "list": [anime for anime in result],
        }

    return {"query": search.query}
