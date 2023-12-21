from fastapi import UploadFile
import puremagic


def get_mime_type(file: UploadFile) -> str | None:
    try:
        return puremagic.magic_stream(file.file)[0].mime_type
    except puremagic.PureError:
        return None


def get_mime_extension(mime_type: str) -> str | None:
    return {
        "image/jpeg": "jpg",
        "image/png": "png",
    }.get(mime_type)
