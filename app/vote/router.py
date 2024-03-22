from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import VoteResponse, VoteArgs
from app.dependencies import auth_required
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import Vote
from app import constants
from . import service

from app.models import (
    Collection,
    Comment,
    User,
)

from .dependencies import (
    validate_get_vote,
    validate_content,
)


router = APIRouter(prefix="/vote", tags=["Vote"])


@router.get("/{content_type}/{slug}", response_model=VoteResponse)
async def get_vote(vote: Vote = Depends(validate_get_vote)):
    return vote


@router.put("/{content_type}/{slug}", response_model=VoteResponse)
async def set_vote(
    args: VoteArgs,
    content_type: str,
    content: Collection | Comment = Depends(validate_content),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_VOTE_SET])
    ),
):
    return await service.set_vote(
        session, content_type, content, user, args.score
    )
