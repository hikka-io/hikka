from pydantic import Field, field_validator
from app.schemas import PaginationResponse
from app.utils import is_empty_markdown
from app.schemas import DataTypeMixin
from app.schemas import UserResponse
from app.schemas import CustomModel
from app.schemas import datetime_pd
from app.utils import is_valid_tag
from app import constants
from enum import Enum


# Enums
class ArticleCategoryEnum(str, Enum):
    article_system = constants.ARTICLE_SYSTEM
    article_news = constants.ARTICLE_NEWS


class ArticleContentEnum(str, Enum):
    anime = constants.CONTENT_ANIME
    manga = constants.CONTENT_MANGA
    novel = constants.CONTENT_NOVEL


# Args
class ArticleContentArgs(CustomModel):
    content_type: ArticleContentEnum
    slug: str


class ArticleArgs(CustomModel):
    text: str = Field(min_length=3, max_length=65536)
    title: str = Field(min_length=3, max_length=255)
    content: ArticleContentArgs | None = None
    tags: list[str] = Field(max_length=3)
    draft: bool = Field(default=True)
    category: ArticleCategoryEnum

    @field_validator("tags")
    def validate_tags(cls, tags):
        if not all([is_valid_tag(tag) for tag in tags]):
            raise ValueError("Invalid tag")

        return tags

    @field_validator("text")
    def validate_text(cls, text):
        if is_empty_markdown(text):
            raise ValueError("Field text consists of empty markdown")

        return text


class ArticlesListArgs(CustomModel):
    # content_type: ContentTypeEnum | None = None
    sort: list[str] = ["created:desc"]
    author: str | None = None
    draft: bool = False


# Responses
class ArticleResponse(CustomModel, DataTypeMixin):
    created: datetime_pd
    updated: datetime_pd
    author: UserResponse
    comments_count: int
    cover: str | None
    tags: list[str]
    vote_score: int
    my_score: int
    category: str
    draft: bool
    title: str
    text: str
    slug: str


class ArticlesListResponse(CustomModel):
    pagination: PaginationResponse
    list: list[ArticleResponse]
