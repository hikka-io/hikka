from app.common.schemas.anime import AnimeResponseWithWatch
from app.common.schemas.manga import MangaResponseWithRead
from app.common.schemas.novel import NovelResponseWithRead
from app.schemas import CustomModel
from app import constants
from enum import Enum


# Enums
class RelatedContentTypeEnum(str, Enum):
    content_anime = constants.CONTENT_ANIME
    content_manga = constants.CONTENT_MANGA
    content_novel = constants.CONTENT_NOVEL


# Responses
class FranchiseResponse(CustomModel):
    anime: list[AnimeResponseWithWatch]
    manga: list[MangaResponseWithRead]
    novel: list[NovelResponseWithRead]
