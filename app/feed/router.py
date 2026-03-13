from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from app.schemas import CollectionResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from .schemas import FeedArgs
from app.models import User
from app import constants
from . import service

# TODO: remove me
from app.articles.schemas import ArticlePreviewResponse
from app.comments.schemas import CommentResponse


router = APIRouter(prefix="/feed", tags=["Feed"])


@router.post(
    "",
    response_model=list[
        ArticlePreviewResponse | CommentResponse | CollectionResponse
    ],
)
async def get_feed(
    args: FeedArgs,
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(
        auth_required(
            optional=True,
            scope=[constants.SCOPE_READ_FEED],
        )
    ),
):
    return await service.get_user_feed(session, request_user, args)
