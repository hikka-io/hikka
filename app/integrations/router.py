from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import validate_mal_anime
from fastapi import APIRouter, Depends
from app.schemas import AnimeResponse
from app.database import get_session
from .schemas import MALAnimeArgs
from app.models import Anime
from . import service


router = APIRouter(prefix="/integrations", tags=["Integrations"])


@router.get("/mal/anime/{mal_id}", response_model=AnimeResponse)
async def mal_anime(anime: Anime = Depends(validate_mal_anime)):
    return anime


@router.post("/mal/anime", response_model=list[AnimeResponse | None])
async def mal_anime_list(
    args: MALAnimeArgs, session: AsyncSession = Depends(get_session)
):
    return await service.get_by_mal_ids(session, args)
