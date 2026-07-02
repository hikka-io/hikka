from typing import Literal
from app import constants


# Literals
FeedContentTypes = Literal[
    constants.CONTENT_COLLECTION,
    constants.CONTENT_ARTICLE,
    constants.CONTENT_COMMENT,
    constants.CONTENT_REVIEW,
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
    constants.CONTENT_SYSTEM_EDIT,
    constants.CONTENT_COLLECTION,
    constants.CONTENT_CHARACTER,
    constants.CONTENT_ARTICLE,
    constants.CONTENT_PERSON,
    constants.CONTENT_ANIME,
    constants.CONTENT_MANGA,
    constants.CONTENT_NOVEL,
]

ReviewContentTypes = Literal[
    constants.CONTENT_ANIME,
    constants.CONTENT_MANGA,
    constants.CONTENT_NOVEL,
]
