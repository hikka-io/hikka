from pydantic import Field, field_validator
from app.utils import is_empty_markdown
from .utils import is_valid_tag
from datetime import datetime
from app import constants
from enum import Enum

from app.schemas import (
    PaginationResponse,
    CharacterResponse,
    PersonResponse,
    AnimeResponse,
    UserResponse,
    CustomModel,
)


# Enums
class ContentTypeEnum(str, Enum):
    content_character = constants.CONTENT_CHARACTER
    content_person = constants.CONTENT_PERSON
    content_anime = constants.CONTENT_ANIME


# Args
class CollectionContentArgs(CustomModel):
    comment: str | None = None
    label: str | None = None
    order: int
    slug: str


class CollectionArgs(CustomModel):
    content: list[CollectionContentArgs] = Field(min_length=1, max_length=500)
    title: str = Field(min_length=3, max_length=255)
    tags: list[str] = Field(max_length=8)
    content_type: ContentTypeEnum
    description: str | None
    labels_order: list[str]
    private: bool
    spoiler: bool
    nsfw: bool

    @field_validator("tags")
    def validate_tags(cls, tags):
        if not all([is_valid_tag(tag) for tag in tags]):
            raise ValueError("Invalid tag")

        return tags

    @field_validator("labels_order")
    def validate_labels_order(cls, labels_order):
        if len(list(set(labels_order))) != len(labels_order):
            raise ValueError("Label order duplicates")

        return labels_order

    @field_validator("description")
    def validate_description(cls, description):
        if is_empty_markdown(description):
            raise ValueError("Field description consists of empty markdown")

        return description


# Responses
class CollectionResponse(CustomModel):
    author: UserResponse
    created: datetime
    updated: datetime
    description: str
    tags: list[str]
    reference: str
    spoiler: bool
    entries: int
    title: str
    nsfw: bool


class CollectionsListResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CollectionResponse]


class CollectionContentResponse(CustomModel):
    content: AnimeResponse | CharacterResponse | PersonResponse
    order: int


class CollectionInfoResponse(CollectionResponse):
    content: list[CollectionContentResponse]
    pass
