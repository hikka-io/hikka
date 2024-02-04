from .dependencies import validate_watari_anime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import Anime
from . import service

from app.schemas import (
    AnimeExternalResponse,
    AnimeVideoResponse,
    AnimeStaffResponse,
    CharacterResponse,
    AnimeResponse,
)


router = APIRouter(prefix="/integrations", tags=["Integrations"])


@router.get("/watari/{slug}/characters", response_model=list[CharacterResponse])
async def watari_characters(
    anime: Anime = Depends(validate_watari_anime),
    session: AsyncSession = Depends(get_session),
):
    return await service.get_main_characters(session, anime)


@router.get("/watari/{slug}/staff", response_model=list[AnimeStaffResponse])
async def watari_staff(
    anime: Anime = Depends(validate_watari_anime),
    session: AsyncSession = Depends(get_session),
):
    staff = await service.get_anime_main_staff(session, anime)
    return staff.unique().all()


@router.get("/watari/{slug}/videos", response_model=list[AnimeVideoResponse])
async def watari_videos(anime: Anime = Depends(validate_watari_anime)):
    return anime.videos[:8]


@router.get(
    "/watari/{slug}/external",
    response_model=list[AnimeExternalResponse],
)
async def watari_external(anime: Anime = Depends(validate_watari_anime)):
    return anime.external[:8]


@router.get("/watari/{slug}", response_model=AnimeResponse)
async def watari_anime(anime: Anime = Depends(validate_watari_anime)):
    return anime
