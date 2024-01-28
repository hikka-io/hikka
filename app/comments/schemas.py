from dataclasses import dataclass, field
from app.models import Comment
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
class CommentTextArgs(CustomModel):
    text: str = Field(min_length=1, max_length=2048)


class CommentArgs(CommentTextArgs):
    parent: UUID | None = None


# Responses
class CommentResponse(CustomModel):
    replies: list["CommentResponse"] = []
    total_replies: int = 0
    author: UserResponse
    updated: datetime
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
@dataclass
class CommentNode:
    # Reference is default field of data class, do not move it
    reference: str

    replies: list["CommentNode"] = field(default_factory=list)
    total_replies: int = 0
    hidden: bool = False
    created: str = None
    author: str = None
    score: int = None
    depth: int = None
    text: str = None

    def from_comment(self, comment: Comment):
        self.text = comment.text if not comment.hidden else None
        self.updated = comment.created
        self.created = comment.created
        self.author = comment.author
        self.hidden = comment.hidden
        self.score = comment.score
        self.depth = comment.depth
        return self

    @classmethod
    def create(cls, reference: str, comment: Comment = None):
        node_instance = cls(reference)
        node_instance.reference = reference

        if comment:
            node_instance = node_instance.from_comment(comment)

        return node_instance
