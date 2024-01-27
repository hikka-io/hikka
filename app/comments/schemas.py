from datetime import datetime
from pydantic import Field
from app import constants
from uuid import UUID
from enum import Enum

from app.schemas import (
    PaginationResponse,
    UserResponse,
    CustomModel,
)


# Enums
class ContentTypeEnum(str, Enum):
    content_edit = constants.CONTENT_SYSTEM_EDIT


# Args
class CommentArgs(CustomModel):
    text: str = Field(min_length=1, max_length=2048)
    parent: UUID | None = None


# Responses
class CommentResponse(CustomModel):
    replies: list["CommentResponse"] = []
    author: UserResponse
    total_replies: int
    created: datetime
    text: str | None
    reference: str
    hidden: bool
    score: int
    depth: int


class CommentListResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CommentResponse]


# Misc
class CommentNode:
    def __init__(
        self,
        reference,
        text=None,
        author=None,
        created=None,
        score=None,
        depth=None,
        hidden=False,
    ):
        self.reference = reference
        self.created = created
        self.total_replies = 0
        self.author = author
        self.replies = []
        self.text = text
        self.score = score
        self.depth = depth
        self.hidden = hidden
