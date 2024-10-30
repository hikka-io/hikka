from .schemas import ArticleArgs, ArticleResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User
from app import constants
from . import service


router = APIRouter(prefix="/articles", tags=["Articles"])


@router.post("/create", response_model=ArticleResponse)
async def create_collection(
    args: ArticleArgs,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_COLLECTION_CREATE],
            scope=[constants.SCOPE_CREATE_ARTICLE],
        )
    ),
):
    return await service.create_article(session, args, user)
