from .dependencies import verify_content_franchise
from app.models import User, Anime, Manga, Novel
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from .schemas import FranchiseResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from . import service


router = APIRouter(prefix="/related", tags=["Related"])


@router.get(
    "/{content_type}/{slug}/franchise",
    response_model=FranchiseResponse,
    summary="Franchise",
)
async def content_franchise(
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(auth_required(optional=True)),
    content: Anime | Manga | Novel = Depends(verify_content_franchise),
):
    return await service.get_franchise(session, content, request_user)
