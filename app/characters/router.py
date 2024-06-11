from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_page, get_size
from app.dependencies import auth_required
from app.schemas import QuerySearchArgs
from .dependencies import get_character
from fastapi import APIRouter, Depends
from app.models import Character, User
from app.database import get_session
from app import meilisearch
from app import constants
from . import service

from .schemas import (
    CharactersSearchPaginationResponse,
    CharacterVoicesPaginationResponse,
    CharacterAnimePaginationResponse,
    CharacterMangaPaginationResponse,
    CharacterNovelPaginationResponse,
    CharacterCountResponse,
)

from app.utils import (
    pagination_dict,
    pagination,
)


router = APIRouter(prefix="/characters", tags=["Characters"])


@router.get("/{slug}", response_model=CharacterCountResponse)
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
    request_user: User | None = Depends(auth_required(optional=True)),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.character_anime_total(session, character)
    anime = await service.character_anime(
        session, character, request_user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": anime.unique().all(),
    }


@router.get("/{slug}/manga", response_model=CharacterMangaPaginationResponse)
async def character_manga(
    session: AsyncSession = Depends(get_session),
    character: Character = Depends(get_character),
    request_user: User | None = Depends(auth_required(optional=True)),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.character_manga_total(session, character)
    manga = await service.character_manga(
        session, character, request_user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": manga.unique().all(),
    }


@router.get("/{slug}/novel", response_model=CharacterNovelPaginationResponse)
async def character_novel(
    session: AsyncSession = Depends(get_session),
    character: Character = Depends(get_character),
    request_user: User | None = Depends(auth_required(optional=True)),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.character_novel_total(session, character)
    novel = await service.character_novel(
        session, character, request_user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": novel.unique().all(),
    }


@router.get("/{slug}/voices", response_model=CharacterVoicesPaginationResponse)
async def character_voices(
    session: AsyncSession = Depends(get_session),
    character: Character = Depends(get_character),
    request_user: User | None = Depends(auth_required(optional=True)),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.character_voices_total(session, character)
    anime = await service.character_voices(
        session, character, request_user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": anime.unique().all(),
    }
