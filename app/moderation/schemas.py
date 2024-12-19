from enum import Enum
from pydantic import field_validator
from app import constants
from app.schemas import PaginationResponse, CustomModel
from app.schemas import datetime_pd


# Responses
class ModerationResponse(CustomModel):
    target_type: str
    created: datetime_pd
    reference: str
    data: dict


class ModerationPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[ModerationResponse]


# Enums
class ModerationTypeEnum(str, Enum):
    edit_accepted = constants.MODERATION_EDIT_ACCEPTED
    edit_denied = constants.MODERATION_EDIT_DENIED
    edit_updated = constants.MODERATION_EDIT_UPDATED
    comment_hidden = constants.MODERATION_COMMENT_HIDDEN
    collection_deleted = constants.MODERATION_COLLECTION_DELETED
    collection_updated = constants.MODERATION_COLLECTION_UPDATED


# Args
class ModerationSearchArgs(CustomModel):
    sort: str = "created:desc"
    target_type: ModerationTypeEnum | None = None
    author: str | None = None

    @field_validator("sort")
    def validate_sort(cls, sort):
        valid_orders = ["asc", "desc"]
        valid_fields = [
            "created",
        ]

        parts = sort.split(":")

        if len(parts) != 2:
            raise ValueError(f"Invalid sort format: {sort}")

        field, order = parts

        if field not in valid_fields or order not in valid_orders:
            raise ValueError(f"Invalid sort value: {sort}")

        return sort
