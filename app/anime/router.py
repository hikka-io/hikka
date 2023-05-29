from .dependencies import get_anime_info
from .schemas import AnimeInfoResponse
from fastapi import APIRouter, Depends
from app.models import Anime


router = APIRouter(prefix="/anime", tags=["Anime"])


@router.get("/{slug}", response_model=AnimeInfoResponse)
async def anime_slug(anime: Anime = Depends(get_anime_info)):
    return anime
