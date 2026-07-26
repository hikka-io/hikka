from app.common.schemas.reviews import ReviewRecommended
from app.common.schemas.comments import CommentResponse
from app.schemas import PaginationResponse, CustomModel
from app.common.schemas.reviews import ReviewArgs
from pydantic import Field, field_validator
from app.utils import is_empty_markdown
from typing import Literal
from app import utils
from uuid import UUID

from app.models import (
    Collection,
    Character,
    Article,
    Person,
    Anime,
    Manga,
    Novel,
    Edit,
)


# Types
CommentableType = (
    Collection | Character | Article | Person | Anime | Manga | Novel | Edit
)

CommentType = Literal["all", "comment", "review"]


# Args
class CommentTextArgs(CustomModel):
    text: str = Field(min_length=1, max_length=2048)
    review: ReviewArgs | None = None

    @field_validator("text")
    def validate_text(cls, text):
        text = text.strip("\n")

        if is_empty_markdown(text):
            raise ValueError("Field text consists of empty markdown")

        return text


class CommentArgs(CommentTextArgs):
    parent: UUID | None = None


class CommentsFilterArgs(CustomModel):
    recommended: ReviewRecommended | None = None
    comment_type: CommentType = "all"
    sort: list[str] = ["created:desc"]

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        return utils.check_sort(
            sort_list,
            [
                "total_replies",
                "created",
                "updated",
                "score",
            ],
        )


class UserCommentsFilterArgs(CommentsFilterArgs):
    first_level_only: bool = False


# Responses
class CommentListResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CommentResponse]
