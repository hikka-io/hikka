from app.common.schemas.comments import CommentResponse
from app.schemas import PaginationResponse, CustomModel
from app.common.schemas.reviews import ReviewArgs
from pydantic import Field, field_validator
from app.utils import is_empty_markdown
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


# Responses
class CommentListResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CommentResponse]
