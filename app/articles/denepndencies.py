from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import round_datetime, utcnow
from app.dependencies import auth_required
from app.database import get_session
from app.service import count_logs
from app.errors import Abort
from app.models import User
from fastapi import Depends
from app import constants


async def validate_rate_limit(
    session: AsyncSession = Depends(get_session),
    author: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_ARTICLE_CREATE],
            scope=[constants.SCOPE_CREATE_ARTICLE],
        )
    ),
):
    # TODO: Make reusable code for rate limit (?)

    # For now we will allow 10 articles per hour
    articles_limit = 10
    logs_count = await count_logs(
        session,
        constants.LOG_ARTICLE_CREATE,
        autor,
        start_time=round_datetime(utcnow(), hours=1),
    )

    if (
        author.role
        not in [
            constants.ROLE_ADMIN,
        ]
        and logs_count > articles_limit
    ):
        raise Abort("articles", "rate-limit")

    return author
