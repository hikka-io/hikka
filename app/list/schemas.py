from app.schemas import PaginationResponse
from app.schemas import ORJSONModel
from datetime import datetime
from typing import Union


# Responses
class AnimeResponse(ORJSONModel):
    title_ua: Union[str, None]
    title_en: Union[str, None]
    title_ja: Union[str, None]
    episodes: Union[int, None]
    status: Union[str, None]
    scored_by: int
    score: float


class WatchResponse(ORJSONModel):
    note: Union[str, None]
    anime: AnimeResponse
    updated: datetime
    created: datetime
    reference: str
    episodes: int
    status: str
    score: int


class WatchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[WatchResponse]
