from pydantic import Field
from app import constants
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
    text: str = Field(max_length=140)


# Responses
class CommentResponse(CustomModel):
    replies: list["CommentResponse"] = []
    author: UserResponse
    total_replies: int
    reference: str
    text: str


class CommentListResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CommentResponse]


# Misc
class CommentNode:
    def __init__(self, reference, text=None, author=None):
        self.reference = reference
        self.total_replies = 0
        self.author = author
        self.replies = []
        self.text = text
