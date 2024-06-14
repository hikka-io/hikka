from app.schemas import PaginationResponse
from app.schemas import CustomModel
from app.schemas import datetime_pd


# Args
class EventArgs(CustomModel):
    r: str | None
    d: str
    n: str
    u: str


# Responses
class ImageResponse(CustomModel):
    created: datetime_pd
    path: str


class ImagesPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[ImageResponse]
