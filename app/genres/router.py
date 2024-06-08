from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import GenreListResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from . import service


router = APIRouter(prefix="/genres", tags=["Genres"])


@router.get(
    "",
    response_model=GenreListResponse,
    summary="Genres list",
)
async def genres(session: AsyncSession = Depends(get_session)):
    genres = await service.get_genres(session)
    return {"list": genres.all()}
