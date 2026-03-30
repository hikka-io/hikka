from app.schemas import FollowUserResponse, CustomModel
from datetime import datetime
from typing import Literal
from app import constants

# TODO: remove me
from app.comments.schemas import CommentResponse


# Args
class FeedArgs(CustomModel):
    before: datetime | None = None
    content_type: (
        Literal[
            constants.CONTENT_COLLECTION,
            constants.CONTENT_ARTICLE,
            constants.CONTENT_COMMENT,
        ]
        | None
    ) = None


# Responses
class CommentResponseFeed(CommentResponse):
    author: FollowUserResponse
