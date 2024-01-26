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
    text: str = Field(max_length=2048)
    parent: UUID | None = None


# Responses
class CommentResponse(CustomModel):
    replies: list["CommentResponse"] = []
    author: UserResponse
    total_replies: int
    created: datetime
    reference: str
    score: int
    depth: int
    text: str


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
    ):
        self.reference = reference
        self.created = created
        self.total_replies = 0
        self.author = author
        self.replies = []
        self.text = text
        self.score = score
        self.depth = depth
