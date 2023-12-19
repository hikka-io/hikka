from fastapi import UploadFile
import puremagic


def get_mime_type(file: UploadFile) -> str | None:
    try:
        return puremagic.magic_stream(file.file)[0].mime_type
    except puremagic.PureError:
        return None
