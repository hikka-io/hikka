from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import get_character
from app.schemas import QuerySearchArgs
from fastapi import APIRouter, Depends
from app.dependencies import get_page
from app.database import get_session
from app.models import Character
from app import constants
from . import meilisearch
from . import service


from .schemas import (
    CharactersSearchPaginationResponse,
    CharacterAnimePaginationResponse,
)

from app.utils import (
    pagination_dict,
    pagination,
)


router = APIRouter(prefix="/characters", tags=["Characters"])


@router.post("", response_model=CharactersSearchPaginationResponse)
async def search_characters(
    search: QuerySearchArgs,
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


@router.get("/{slug}/anime", response_model=CharacterAnimePaginationResponse)
async def character_anime(
    page: int = Depends(get_page),
    character: Character = Depends(get_character),
    session: AsyncSession = Depends(get_session),
):
    total = await service.character_anime_total(session, character)

    limit, offset = pagination(page, limit=constants.SEARCH_RESULT_LIMIT)

    result = await service.character_anime(session, character, limit, offset)

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": [entry for entry in result],
    }
