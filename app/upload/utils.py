from datetime import datetime, timedelta
from fastapi import UploadFile
import puremagic


def get_mime_type(file: UploadFile) -> str | None:
    try:
        return puremagic.magic_stream(file.file)[0].mime_type
    except puremagic.PureError:
        return None


def get_mime_extension(mime_type: str) -> str | None:
    return {
        "image/webp": "webp",
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/gif": "gif",
    }.get(mime_type)


def round_day(now: datetime) -> datetime:
    return now - timedelta(
        days=now.day % 1,
        hours=now.hour,
        minutes=now.minute,
        seconds=now.second,
        microseconds=now.microsecond,
    )
