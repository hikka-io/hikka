from app.common.schemas.reviews import ReviewResponse
from dataclasses import dataclass, field
from app.models import Review, User
from app.utils import path_to_uuid
from app.models import Comment
from datetime import datetime
from typing import Literal
from app import constants
from enum import Enum

from app.schemas import (
    UserResponse,
    CustomModel,
    datetime_pd,
)


# Enums
class CommentContentTypeEnum(str, Enum):
    content_collection = constants.CONTENT_COLLECTION
    content_character = constants.CONTENT_CHARACTER
    content_edit = constants.CONTENT_SYSTEM_EDIT
    content_article = constants.CONTENT_ARTICLE
    content_person = constants.CONTENT_PERSON
    content_anime = constants.CONTENT_ANIME
    content_manga = constants.CONTENT_MANGA
    content_novel = constants.CONTENT_NOVEL


# Responses
class CommentResponse(CustomModel):
    data_type: Literal["comment"]
    replies: list["CommentResponse"] = []
    review: ReviewResponse | None = None
    total_replies: int = 0
    updated: datetime_pd
    created: datetime_pd
    author: UserResponse
    parent: str | None
    content_type: CommentContentTypeEnum
    is_editable: bool
    text: str | None
    vote_score: int
    reference: str
    my_score: int
    preview: dict
    hidden: bool
    depth: int


# Misc
@dataclass
class CommentNode:
    # Reference is default field of data class, do not move it
    reference: str
    data_type: str = "comment"

    replies: list["CommentNode"] = field(default_factory=list)
    content_type: str | None = None
    created: datetime | None = None
    review: Review | None = None
    preview: dict | None = None
    author: User | None = None
    is_editable: bool = False
    parent: str | None = None
    text: str | None = None
    total_replies: int = 0
    hidden: bool = False
    vote_score: int = 0
    my_score: int = 0
    score: int = 0
    depth: int = 0

    def from_comment(self, comment: Comment):
        # Bit hackish but should work
        self.review = comment.review if "review" in comment.__dict__ else None

        self.is_editable = comment.is_editable if not comment.hidden else False
        self.my_score = comment.my_score if comment.my_score else 0
        self.text = comment.text if not comment.hidden else None
        self.total_replies = comment.total_replies
        self.content_type = comment.content_type
        self.vote_score = comment.vote_score
        self.preview = comment.preview
        self.updated = comment.updated
        self.created = comment.created
        self.author = comment.author
        self.hidden = comment.hidden
        self.depth = comment.depth

        if len(comment.path) > 1:
            self.parent = path_to_uuid(comment.path[-2])

        return self

    @classmethod
    def create(cls, reference: str, comment: Comment = None):
        node_instance = cls(reference)
        node_instance.reference = reference

        if comment:
            node_instance = node_instance.from_comment(comment)

        return node_instance
