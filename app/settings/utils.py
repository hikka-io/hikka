from app import constants


def get_anime_import_status(raw_status: str) -> str:
    """Convert MAL's status to out internal format"""

    return {
        "Completed": constants.WATCH_COMPLETED,
        "Watching": constants.WATCH_WATCHING,
        "Plan to Watch": constants.WATCH_PLANNED,
        "On-Hold": constants.WATCH_ON_HOLD,
        "Dropped": constants.WATCH_DROPPED,
    }.get(raw_status)
