from .schemas import AnimeScheduleArgs
from app.errors import Abort


async def validate_schedule_args(args: AnimeScheduleArgs):
    # ToDo: there should be better way to write this check
    if args.airing_range is not None and args.airing_season is not None:
        raise Abort("schedule", "incompatible-filters")

    return args
