from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_page, get_size
from app.schemas import QuerySearchArgs
from .dependencies import get_character
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import Character
from app import meilisearch
from app import constants
from . import service

from .schemas import (
    CharactersSearchPaginationResponse,
    CharacterVoicesPaginationResponse,
    CharacterAnimePaginationResponse,
    CharacterFullResponse,
)

from app.utils import (
    pagination_dict,
    pagination,
)


router = APIRouter(prefix="/characters", tags=["Characters"])


@router.get("/{slug}", response_model=CharacterFullResponse)
async def character_info(character: Character = Depends(get_character)):
    return character


@router.post("", response_model=CharactersSearchPaginationResponse)
async def search_characters(
    search: QuerySearchArgs,
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    if not search.query:
        limit, offset = pagination(page, size)
        total = await service.search_total(session)
        characters = await service.characters_search(session, limit, offset)
        return {
            "pagination": pagination_dict(total, page, limit),
            "list": characters.all(),
        }

    return await meilisearch.search(
        constants.SEARCH_INDEX_CHARACTERS,
        sort=["favorites:desc"],
        query=search.query,
        page=page,
        size=size,
    )


@router.get("/{slug}/anime", response_model=CharacterAnimePaginationResponse)
async def character_anime(
    session: AsyncSession = Depends(get_session),
    character: Character = Depends(get_character),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.character_anime_total(session, character)
    anime = await service.character_anime(session, character, limit, offset)
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": anime.all(),
    }


@router.get(
    "/{slug}/voices",
    response_model=CharacterVoicesPaginationResponse,
)
async def character_voices(
    session: AsyncSession = Depends(get_session),
    character: Character = Depends(get_character),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.character_voices_total(session, character)
    anime = await service.character_voices(session, character, limit, offset)
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": anime.all(),
    }
