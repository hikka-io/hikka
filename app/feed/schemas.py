from app.common.schemas.comments import CommentResponse
from app.schemas import FollowUserResponse, CustomModel
from datetime import datetime
from typing import Literal
from app import constants


# Literals
FeedContentTypes = Literal[
    constants.CONTENT_COLLECTION,
    constants.CONTENT_ARTICLE,
    constants.CONTENT_COMMENT,
]

CollectionContentTypes = Literal[
    constants.CONTENT_CHARACTER,
    constants.CONTENT_PERSON,
    constants.CONTENT_ANIME,
    constants.CONTENT_MANGA,
    constants.CONTENT_NOVEL,
]

ArticleCategories = Literal[
    constants.ARTICLE_ORIGINAL,
    constants.ARTICLE_REVIEWS,
    constants.ARTICLE_NEWS,
]

ArticleContentTypes = Literal[
    constants.CONTENT_ANIME,
    constants.CONTENT_MANGA,
    constants.CONTENT_NOVEL,
    constants.NO_CONTENT,
]

CommentContentTypes = Literal[
    constants.CONTENT_COLLECTION,
    constants.CONTENT_CHARACTER,
    constants.CONTENT_SYSTEM_EDIT,
    constants.CONTENT_ARTICLE,
    constants.CONTENT_PERSON,
    constants.CONTENT_ANIME,
    constants.CONTENT_MANGA,
    constants.CONTENT_NOVEL,
]


# Args
class FeedArgs(CustomModel):
    # TODO: remove me
    content_type: FeedContentTypes | None = None

    collection_content_types: list[CollectionContentTypes] | None = None
    comment_content_types: list[CommentContentTypes] | None = None
    article_content_types: list[ArticleContentTypes] | None = None
    article_categories: list[ArticleCategories] | None = None
    feed_content_types: list[FeedContentTypes] | None = None
    before: datetime | None = None
    only_followed: bool = False


# Responses
class CommentResponseFeed(CommentResponse):
    author: FollowUserResponse
