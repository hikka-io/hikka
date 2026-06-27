from app.schemas import datetime_pd
from app import constants
from enum import Enum

from app.schemas import (
    PaginationResponse,
    AnimeResponse,
    MangaResponse,
    NovelResponse,
    UserResponse,
    CustomModel,
)


# Enums
class HistoryTypeEnum(str, Enum):
    watch = constants.HISTORY_WATCH
    watch_delete = constants.HISTORY_WATCH_DELETE
    read_manga = constants.HISTORY_READ_MANGA
    read_manga_delete = constants.HISTORY_READ_MANGA_DELETE
    read_novel = constants.HISTORY_READ_NOVEL
    read_novel_delete = constants.HISTORY_READ_NOVEL_DELETE
    watch_import = constants.HISTORY_WATCH_IMPORT
    read_import = constants.HISTORY_READ_IMPORT
    favourite_anime_add = constants.HISTORY_FAVOURITE_ANIME
    favourite_anime_remove = constants.HISTORY_FAVOURITE_ANIME_REMOVE
    favourite_manga_add = constants.HISTORY_FAVOURITE_MANGA
    favourite_manga_remove = constants.HISTORY_FAVOURITE_MANGA_REMOVE
    favourite_novel_add = constants.HISTORY_FAVOURITE_NOVEL
    favourite_novel_remove = constants.HISTORY_FAVOURITE_NOVEL_REMOVE


# Responses
class HistoryResponse(CustomModel):
    content: AnimeResponse | MangaResponse | NovelResponse | None = None
    created: datetime_pd
    updated: datetime_pd
    user: UserResponse
    history_type: HistoryTypeEnum
    reference: str
    data: dict


class HistoryPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[HistoryResponse]
