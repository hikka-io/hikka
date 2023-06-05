from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app import constants
from . import meilisearch
from . import service

from .schemas import (
    CharactersSearchPaginationResponse,
    CharactersSearchArgs,
)

from app.utils import (
    pagination_dict,
    pagination,
)


router = APIRouter(prefix="/characters", tags=["Characters"])


@router.post("", response_model=CharactersSearchPaginationResponse)
async def search_characters(
    search: CharactersSearchArgs,
    session: AsyncSession = Depends(get_session),
):
    if not search.query:
        total = await service.search_total(session)

        limit, offset = pagination(
            search.page,
            limit=constants.SEARCH_RESULT_LIMIT,
        )

        result = await service.characters_search(session, limit, offset)

        return {
            "pagination": pagination_dict(total, search.page, limit),
            "list": [character for character in result],
        }

    return await meilisearch.characters_search(search)
