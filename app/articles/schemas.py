from pydantic import Field, field_validator
from app.utils import is_empty_markdown
from app.utils import is_valid_tag
from app.utils import check_sort
from app import constants
from enum import Enum

from app.schemas import (
    PaginationResponse,
    FollowUserResponse,
    DataTypeMixin,
    CustomModel,
    datetime_pd,
)


# Enums
class ArticleCategoryEnum(str, Enum):
    article_system = constants.ARTICLE_SYSTEM
    article_reviews = constants.ARTICLE_REVIEWS
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
    cover: str | None = None
    trusted: bool = False

    @field_validator("tags")
    def validate_tags(cls, tags):
        # Removing duplicates
        tags = list(set(tags))

        if not all([is_valid_tag(tag) for tag in tags]):
            raise ValueError("Invalid tag")

        return tags

    @field_validator("text")
    def validate_text(cls, text):
        if is_empty_markdown(text):
            raise ValueError("Field text consists of empty markdown")

        return text


class ArticlesListArgs(CustomModel):
    content_type: ArticleContentEnum | None = None
    min_vote_score: int | None = Field(0, ge=0)
    tags: list[str] = Field([], max_length=3)  # TODO: tags mixin (?)
    sort: list[str] = ["created:desc"]
    content_slug: str | None = None
    show_trusted: bool = True
    author: str | None = None
    draft: bool = False

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        return check_sort(
            sort_list,
            [
                "vote_score",
                "created",
            ],
        )


# Responses
class TagResponse(CustomModel):
    content_count: int
    name: str


class ArticleContentResponse(CustomModel, DataTypeMixin):
    image: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    title_ja: str | None
    title_en: str | None
    title_ua: str | None
    slug: str


class ArticleResponse(CustomModel, DataTypeMixin):
    content: ArticleContentResponse | None
    author: FollowUserResponse
    tags: list[TagResponse]
    created: datetime_pd
    updated: datetime_pd
    comments_count: int
    cover: str | None
    vote_score: int
    my_score: int
    category: str
    trusted: bool
    draft: bool
    title: str
    text: str
    slug: str


class ArticlesListResponse(CustomModel):
    pagination: PaginationResponse
    list: list[ArticleResponse]


class UserArticleStatsResponse(CustomModel):
    user: FollowUserResponse
    reviews: int
    news: int


class ArticlesTopResponse(CustomModel):
    authors: list[UserArticleStatsResponse]
    tags: list[TagResponse]
