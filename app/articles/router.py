from .schemas import ArticleArgs, ArticleResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from app.schemas import SuccessResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User, Article
from app import constants
from . import service

from .dependencies import (
    validate_article_create,
    validate_article_update,
    validate_article_delete,
    validate_article,
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


@router.delete("/{slug}", response_model=SuccessResponse)
async def delete_article(
    article: Article = Depends(validate_article_delete),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_ARTICLE_DELETE],
            scope=[constants.SCOPE_DELETE_ARTICLE],
        )
    ),
):
    await service.delete_article(session, article, user)
    return {"success": True}


@router.get("/{slug}", response_model=ArticleResponse)
async def get_article(article: Article = Depends(validate_article)):
    return article
