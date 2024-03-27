from pydantic import Field, field_validator
from app.utils import is_empty_markdown
from .utils import is_valid_tag
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


# Args
class CollectionContentArgs(CustomModel):
    comment: str | None = Field(default=None, min_length=3)
    label: str | None = Field(default=None, min_length=1)
    order: int
    slug: str


class CollectionsListArgs(CustomModel):
    sort: list[str] = ["system_ranking:desc", "created:desc"]
    content_type: ContentTypeEnum | None = None
    author: str | None = None
    only_public: bool = True

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        valid_orders = ["asc", "desc"]
        valid_fields = [
            "system_ranking",
            "created",
        ]

        if len(sort_list) != len(set(sort_list)):
            raise ValueError("Invalid sort: duplicates")

        for sort_item in sort_list:
            parts = sort_item.split(":")

            if len(parts) != 2:
                raise ValueError(f"Invalid sort format: {sort_item}")

            field, order = parts

            if field not in valid_fields or order not in valid_orders:
                raise ValueError(f"Invalid sort value: {sort_item}")

        return sort_list


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
class CollectionsListResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CollectionResponse]
