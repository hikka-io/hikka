from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import SuccessResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from app import constants
from . import service

from app.utils import (
    pagination_dict,
    pagination,
)

from app.models import (
    Article,
    Anime,
    Manga,
    Novel,
    User,
)

from .schemas import (
    ArticlesListResponse,
    ArticlesListArgs,
    ArticleResponse,
    ArticleArgs,
)

from .dependencies import (
    validate_articles_list_args,
    validate_article_content,
    validate_article_create,
    validate_article_update,
    validate_article_delete,
    validate_article,
)

from app.dependencies import (
    auth_required,
    get_page,
    get_size,
)


router = APIRouter(prefix="/articles", tags=["Articles"])


@router.post("/create", response_model=ArticleResponse)
async def create_article(
    args: ArticleArgs,
    session: AsyncSession = Depends(get_session),
    author: User = Depends(validate_article_create),
    content: Anime | Manga | Novel | None = Depends(validate_article_content),
):
    return await service.create_article(session, args, author, content)


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


@router.post("", response_model=ArticlesListResponse)
async def get_articles(
    args: ArticlesListArgs = Depends(validate_articles_list_args),
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
    request_user: User | None = Depends(
        auth_required(
            scope=[constants.SCOPE_READ_COLLECTIONS],
            optional=True,
        )
    ),
):
    limit, offset = pagination(page, size)
    total = await service.get_articles_count(session, request_user, args)
    articles = await service.get_articles(
        session, request_user, args, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": articles.unique().all(),
    }
