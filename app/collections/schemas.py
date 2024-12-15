from pydantic import Field, field_validator
from app.utils import is_empty_markdown
from app.utils import is_valid_tag
from app.utils import check_sort
from app import constants
from enum import Enum

from app.schemas import (
    CollectionVisibilityEnum,
    CollectionResponse,
    PaginationResponse,
    CustomModel,
)


# Enums
class ContentTypeEnum(str, Enum):
    content_character = constants.CONTENT_CHARACTER
    content_person = constants.CONTENT_PERSON
    content_anime = constants.CONTENT_ANIME
    content_manga = constants.CONTENT_MANGA
    content_novel = constants.CONTENT_NOVEL


# Args
class CollectionContentArgs(CustomModel):
    comment: str | None = Field(default=None, min_length=3)
    label: str | None = Field(default=None, min_length=1)
    order: int
    slug: str


class CollectionsListArgs(CustomModel):
    sort: list[str] = ["system_ranking:desc", "created:desc"]
    content: list[str] = Field([], max_length=1)
    content_type: ContentTypeEnum | None = None
    author: str | None = None
    only_public: bool = True

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        return check_sort(
            sort_list,
            [
                "system_ranking",
                "created",
            ],
        )


class CollectionArgs(CustomModel):
    description: str = Field(min_length=3, max_length=65536)
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
class CollectionsListResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CollectionResponse]
