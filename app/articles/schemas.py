from pydantic import ValidationError, Field, field_validator
from app.common.utils import calculate_document_length
from app.common.schemas import Document
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
    article_original = constants.ARTICLE_ORIGINAL
    article_reviews = constants.ARTICLE_REVIEWS
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
    title: str = Field(min_length=3, max_length=255)
    document: list[dict] = Field(min_length=1)
    content: ArticleContentArgs | None = None
    tags: list[str] = Field(max_length=3)
    draft: bool = Field(default=True)
    category: ArticleCategoryEnum
    trusted: bool = False

    @field_validator("document")
    def validate_document_length(cls, document: list[dict]):
        try:
            Document(nodes=document)
        except ValidationError as e:
            raise ValueError(f"Invalid document structure: {e}") from e

        max_length = 65536

        if calculate_document_length(document) > max_length:
            raise ValueError(
                f"Total document length exceeds {max_length} characters"
            )

        return document

    @field_validator("tags")
    def validate_tags(cls, tags):
        # Removing duplicates
        tags = list(set(tags))

        if not all([is_valid_tag(tag) for tag in tags]):
            raise ValueError("Invalid tag")

        return tags


class ArticlesListArgs(CustomModel):
    content_type: ArticleContentEnum | None = None
    min_vote_score: int | None = Field(0, ge=0)
    categories: list[ArticleCategoryEnum] = []
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


class ArticleContentResponseBase(CustomModel, DataTypeMixin):
    image: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    title_en: str | None
    title_ua: str | None
    slug: str


class ArticleAnimeContentResponse(ArticleContentResponseBase):
    title_ja: str | None


class ArticleMangaNovelContentResponse(ArticleContentResponseBase):
    title_original: str | None


class ArticleResponse(CustomModel, DataTypeMixin):
    author: FollowUserResponse
    tags: list[TagResponse]
    created: datetime_pd
    updated: datetime_pd
    document: list[dict]
    comments_count: int
    vote_score: int
    my_score: int
    category: str
    trusted: bool
    draft: bool
    views: int
    title: str
    slug: str

    content: (
        ArticleAnimeContentResponse | ArticleMangaNovelContentResponse | None
    )


class ArticlesListResponse(CustomModel):
    pagination: PaginationResponse
    list: list[ArticleResponse]


class UserArticleStatsResponse(CustomModel):
    user: FollowUserResponse
    total_articles: int
    total_comments: int
    author_score: int
    total_likes: int


class ArticlesTopResponse(CustomModel):
    authors: list[UserArticleStatsResponse]
    tags: list[TagResponse]
