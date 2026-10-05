from app.utils import is_empty_markdown, is_valid_tag, check_sort
from pydantic import Field, field_validator

from app.schemas import (
    CollectionMemberStatusEnum,
    CollectionMemberRoleEnum,
    CollectionContentTypeEnum,
    CollectionVisibilityEnum,
    CollectionResponse,
    PaginationResponse,
    UserResponse,
    CustomModel,
    datetime_pd,
)


# Args
class CollectionContentArgs(CustomModel):
    comment: str | None = Field(default=None, min_length=3)
    label: str | None = Field(default=None, min_length=1)
    order: int
    slug: str


class CollectionsListArgs(CustomModel):
    sort: list[str] = ["system_ranking:desc", "created:desc"]
    content: list[str] = Field([], max_length=1)
    content_type: CollectionContentTypeEnum | None = None
    author: str | None = None
    only_public: bool = True
    tags: list[str] = Field([], max_length=3)

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
    content_type: CollectionContentTypeEnum
    labels_order: list[str]
    spoiler: bool
    nsfw: bool

    updated: int | None = Field(
        None,
        description="Unix timestamp the client started editing from",
        examples=[1686088809],
    )

    @field_validator("tags")
    def validate_tags(cls, tags):
        if not all(is_valid_tag(tag) for tag in tags):
            raise ValueError("Invalid tag")

        return tags

    @field_validator("labels_order")
    def validate_labels_order(cls, labels_order):
        if len(set(labels_order)) != len(labels_order):
            raise ValueError("Label order duplicates")

        return labels_order

    @field_validator("description")
    def validate_description(cls, description):
        description = description.strip("\n")

        if is_empty_markdown(description):
            raise ValueError("Field description consists of empty markdown")

        return description


# Responses
class CollectionsListResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CollectionResponse]

class CollectionMemberResponse(CustomModel):
    status: CollectionMemberStatusEnum
    role: CollectionMemberRoleEnum
    invited_by: UserResponse | None
    owner_offered_at: datetime_pd | None
    created: datetime_pd
    user: UserResponse


class CollectionMembersResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CollectionMemberResponse]
