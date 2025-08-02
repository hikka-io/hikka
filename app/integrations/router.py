from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Anime
from app.models.content.manga import Manga
from app.models.content.novel import Novel
from app.schemas import AnimeResponse, MangaResponse, NovelResponse

from . import service
from .dependencies import (
    validate_anitube_anime,
    validate_mal_content,
)
from .schemas import MALAnimeArgs, MALContentTypeEnum

router = APIRouter(prefix="/integrations", tags=["Integrations"])


@router.get("/anitube/anime/{anitube_id}", response_model=AnimeResponse)
async def anitube_anime(anime: Anime = Depends(validate_anitube_anime)):
    return anime


@router.get(
    "/mal/{content_type}/{mal_id}",
    response_model=AnimeResponse | MangaResponse | NovelResponse,
)
async def mal_content(
    content: Anime | Manga | Novel = Depends(validate_mal_content),
):
    return content


@router.post(
    "/mal/{content_type}",
    response_model=list[AnimeResponse | MangaResponse | NovelResponse | None],
)
async def mal_content_list(
    args: MALAnimeArgs,
    content_type: MALContentTypeEnum,
    session: AsyncSession = Depends(get_session),
):
    return await service.get_by_mal_ids(session, content_type, args)
