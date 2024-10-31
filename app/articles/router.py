from .schemas import ArticleArgs, ArticleResponse
from sqlalchemy.ext.asyncio import AsyncSession
from .denepndencies import validate_rate_limit
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User
from . import service


router = APIRouter(prefix="/articles", tags=["Articles"])


@router.post("/create", response_model=ArticleResponse)
async def create_article(
    args: ArticleArgs,
    session: AsyncSession = Depends(get_session),
    author: User = Depends(validate_rate_limit),
):
    return await service.create_article(session, args, author)
