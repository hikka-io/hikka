from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import get_character
from fastapi import APIRouter, Depends
from app.dependencies import get_page
from app.database import get_session
from app.models import Character
from app import meilisearch
from app import constants
from . import service

from app.schemas import (
    CharacterResponse,
    QuerySearchArgs,
)

from .schemas import (
    CharactersSearchPaginationResponse,
    CharacterAnimePaginationResponse,
)

from app.utils import (
    pagination_dict,
    pagination,
)


router = APIRouter(prefix="/characters", tags=["Characters"])


@router.get("/{slug}", response_model=CharacterResponse)
async def character_info(character: Character = Depends(get_character)):
    return character


@router.post("", response_model=CharactersSearchPaginationResponse)
async def search_characters(
    search: QuerySearchArgs,
    session: AsyncSession = Depends(get_session),
):
    if not search.query:
        limit, offset = pagination(search.page)
        total = await service.search_total(session)
        characters = await service.characters_search(session, limit, offset)
        return {
            "pagination": pagination_dict(total, search.page, limit),
            "list": characters.all(),
        }

    return await meilisearch.search(
        constants.SEARCH_INDEX_CHARACTERS,
        sort=["favorites:desc"],
        query=search.query,
        page=search.page,
    )


@router.get("/{slug}/anime", response_model=CharacterAnimePaginationResponse)
async def character_anime(
    page: int = Depends(get_page),
    character: Character = Depends(get_character),
    session: AsyncSession = Depends(get_session),
):
    limit, offset = pagination(page)
    total = await service.character_anime_total(session, character)
    anime = await service.character_anime(session, character, limit, offset)
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": anime.all(),
    }
