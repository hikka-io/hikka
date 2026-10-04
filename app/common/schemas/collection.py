from app.common.schemas.anime import AnimeResponseWithWatch
from app.common.schemas.manga import MangaResponseWithRead
from app.common.schemas.novel import NovelResponseWithRead
from app.common.schemas.character import CharacterResponse
from app.common.schemas.user import FollowUserResponse
from app.common.schemas.person import PersonResponse
from app.schemas import CustomModel, datetime_pd
from pydantic import field_validator
from typing import Literal
from app import constants
from enum import Enum


# Enums
class CollectionVisibilityEnum(str, Enum):
    visibility_unlisted = constants.COLLECTION_UNLISTED
    visibility_private = constants.COLLECTION_PRIVATE
    visibility_public = constants.COLLECTION_PUBLIC


class CollectionContentTypeEnum(str, Enum):
    content_character = constants.CONTENT_CHARACTER
    content_person = constants.CONTENT_PERSON
    content_anime = constants.CONTENT_ANIME
    content_manga = constants.CONTENT_MANGA
    content_novel = constants.CONTENT_NOVEL


# Responses
class CollectionContentResponse(CustomModel):
    content_type: CollectionContentTypeEnum
    comment: str | None
    label: str | None
    order: int

    content: (
        AnimeResponseWithWatch
        | MangaResponseWithRead
        | NovelResponseWithRead
        | CharacterResponse
        | PersonResponse
    )


class CollectionResponse(CustomModel):
    data_type: Literal["collection"]
    content_type: CollectionContentTypeEnum
    visibility: CollectionVisibilityEnum
    author: FollowUserResponse
    labels_order: list[str]
    created: datetime_pd
    updated: datetime_pd
    comments_count: int
    description: str
    vote_score: int
    tags: list[str]
    reference: str
    my_score: int
    spoiler: bool
    entries: int
    title: str
    nsfw: bool

    collection: list[CollectionContentResponse]

    @field_validator("collection")
    def collection_ordering(cls, collection):
        return sorted(collection, key=lambda c: c.order)
