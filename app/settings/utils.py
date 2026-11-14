from app import constants


def get_anime_import_status(raw_status: str) -> str:
    """Convert MAL's status to out internal format"""

    return {
        "Plan to Watch": constants.WATCH_PLANNED,
        "Completed": constants.WATCH_COMPLETED,
        "Watching": constants.WATCH_WATCHING,
        "On-Hold": constants.WATCH_ON_HOLD,
        "Dropped": constants.WATCH_DROPPED,
    }.get(raw_status)


def get_read_import_status(raw_status: str) -> str:
    """Convert MAL's read status to out internal format"""

    return {
        "Plan to Read": constants.READ_PLANNED,
        "Completed": constants.READ_COMPLETED,
        "Reading": constants.READ_READING,
        "On-Hold": constants.READ_ON_HOLD,
        "Dropped": constants.READ_DROPPED,
    }.get(raw_status)
