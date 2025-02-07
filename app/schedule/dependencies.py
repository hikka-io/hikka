from app.dependencies import auth_required
from .schemas import AnimeScheduleArgs
from app.errors import Abort
from app.models import User
from fastapi import Depends


async def validate_schedule_args(
    args: AnimeScheduleArgs,
    request_user: User | None = Depends(auth_required(optional=True)),
):
    if not request_user and args.only_watch:
        raise Abort("schedule", "watch-no-user")

    return args
