from app.common.schemas.comments import CommentResponse
from app.schemas import PaginationResponse, CustomModel
from pydantic import Field, field_validator
from app.utils import is_empty_markdown
from app import constants
from uuid import UUID
from enum import Enum

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


# Enums
class ContentTypeEnum(str, Enum):
    content_collection = constants.CONTENT_COLLECTION
    content_character = constants.CONTENT_CHARACTER
    content_edit = constants.CONTENT_SYSTEM_EDIT
    content_article = constants.CONTENT_ARTICLE
    content_person = constants.CONTENT_PERSON
    content_anime = constants.CONTENT_ANIME
    content_manga = constants.CONTENT_MANGA
    content_novel = constants.CONTENT_NOVEL


# Args
class CommentTextArgs(CustomModel):
    text: str = Field(min_length=1, max_length=2048)

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
