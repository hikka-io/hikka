from pydantic import Field, field_validator
from app.utils import is_empty_markdown
from .utils import is_valid_tag
from datetime import datetime
from app import constants
from enum import Enum

from app.schemas import (
    AnimeResponseWithWatch,
    PaginationResponse,
    CharacterResponse,
    PersonResponse,
    UserResponse,
    CustomModel,
)


# Enums
class ContentTypeEnum(str, Enum):
    content_character = constants.CONTENT_CHARACTER
    content_person = constants.CONTENT_PERSON
    content_anime = constants.CONTENT_ANIME


class CollectionVisibilityEnum(str, Enum):
    visibility_unlisted = constants.COLLECTION_UNLISTED
    visibility_private = constants.COLLECTION_PRIVATE
    visibility_public = constants.COLLECTION_PUBLIC


# Args
class CollectionContentArgs(CustomModel):
    comment: str | None = Field(default=None, min_length=3)
    label: str | None = Field(default=None, min_length=1)
    order: int
    slug: str


class CollectionArgs(CustomModel):
    description: str = Field(min_length=3, max_length=8192)
    title: str = Field(min_length=3, max_length=255)
    tags: list[str] = Field(max_length=3)
    visibility: CollectionVisibilityEnum
    content: list[CollectionContentArgs]
    content_type: ContentTypeEnum
    labels_order: list[str]
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
class CollectionContentResponse(CustomModel):
    content: AnimeResponseWithWatch | CharacterResponse | PersonResponse
    comment: str | None
    label: str | None
    content_type: str
    order: int


class CollectionResponse(CustomModel):
    visibility: CollectionVisibilityEnum
    labels_order: list[str]
    author: UserResponse
    comments_count: int
    created: datetime
    updated: datetime
    content_type: str
    description: str
    tags: list[str]
    reference: str
    spoiler: bool
    entries: int
    title: str
    nsfw: bool

    collection: list[CollectionContentResponse]

    @field_validator("collection")
    def collection_ordering(cls, collection):
        return sorted(collection, key=lambda c: c.order)


class CollectionsListResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CollectionResponse]
