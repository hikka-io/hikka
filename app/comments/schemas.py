from pydantic import Field, field_validator
from dataclasses import dataclass, field
from app.utils import is_empty_markdown
from app.models import Comment
from datetime import datetime
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
    content_collection = constants.CONTENT_COLLECTION
    content_edit = constants.CONTENT_SYSTEM_EDIT
    content_anime = constants.CONTENT_ANIME


# Args
class CommentVoteArgs(CustomModel):
    score: int = Field(ge=-1, le=1)


class CommentTextArgs(CustomModel):
    text: str = Field(min_length=1, max_length=2048)

    @field_validator("text")
    def validate_text(cls, text):
        if is_empty_markdown(text):
            raise ValueError("Field text consists of empty markdown")

        return text


class CommentArgs(CommentTextArgs):
    parent: UUID | None = None


# Responses
class CommentResponse(CustomModel):
    replies: list["CommentResponse"] = []
    total_replies: int = 0
    author: UserResponse
    is_editable: bool
    updated: datetime
    created: datetime
    text: str | None
    vote_score: int
    reference: str
    my_score: int
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
    is_editable: bool = False
    total_replies: int = 0
    vote_score: int = None
    hidden: bool = False
    my_score: int = None
    created: str = None
    author: str = None
    score: int = None
    depth: int = None
    text: str = None

    def from_comment(self, comment: Comment):
        self.my_score = comment.my_score if comment.my_score else 0
        self.text = comment.text if not comment.hidden else None
        self.is_editable = comment.is_editable
        self.vote_score = comment.vote_score
        self.updated = comment.updated
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
