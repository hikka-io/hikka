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


class FranchiseRelationTypeEnum(str, Enum):
    alternative_setting = constants.RELATION_ALTERNATIVE_SETTING
    alternative_version = constants.RELATION_ALTERNATIVE_VERSION
    side_story = constants.RELATION_SIDE_STORY
    adaptation = constants.RELATION_ADAPTATION
    spin_off = constants.RELATION_SPIN_OFF
    summary = constants.RELATION_SUMMARY
    sequel = constants.RELATION_SEQUEL


# Responses
class FranchiseRelationResponse(CustomModel):
    related_content_type: RelatedContentTypeEnum
    relation_type: FranchiseRelationTypeEnum
    content_type: RelatedContentTypeEnum
    related_slug: str
    slug: str


class FranchiseResponse(CustomModel):
    relations: list[FranchiseRelationResponse]
    anime: list[AnimeResponseWithWatch]
    manga: list[MangaResponseWithRead]
    novel: list[NovelResponseWithRead]
