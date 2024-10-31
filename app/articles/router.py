from .schemas import ArticleArgs, ArticleResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User, Article
from . import service

from .dependencies import (
    validate_article_update,
    validate_article_create,
)


router = APIRouter(prefix="/articles", tags=["Articles"])


@router.post("/create", response_model=ArticleResponse)
async def create_article(
    args: ArticleArgs,
    session: AsyncSession = Depends(get_session),
    author: User = Depends(validate_article_create),
):
    return await service.create_article(session, args, author)


@router.put("/{slug}", response_model=ArticleResponse)
async def update_article(
    args: ArticleArgs,
    article: Article = Depends(validate_article_update),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(auth_required()),
):
    return await service.update_article(session, article, args, user)
