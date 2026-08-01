from app.common.schemas.comments import CommentResponse
from app.schemas import FollowUserResponse, CustomModel
from datetime import datetime

from app.common.schemas.feed import (
    CollectionContentTypes,
    CommentContentTypes,
    ArticleContentTypes,
    ReviewContentTypes,
    ArticleCategories,
    FeedContentTypes,
)


# Args
class FeedArgs(CustomModel):
    collection_content_types: list[CollectionContentTypes] | None = None
    comment_content_types: list[CommentContentTypes] | None = None
    article_content_types: list[ArticleContentTypes] | None = None
    review_content_types: list[ReviewContentTypes] | None = None
    article_categories: list[ArticleCategories] | None = None
    feed_content_types: list[FeedContentTypes] | None = None
    before: datetime | None = None
    only_followed: bool = False


# Responses
class CommentResponseFeed(CommentResponse):
    author: FollowUserResponse
