from pydantic import Field
from typing import Literal

from app.schemas import (
    FollowUserResponse,
    CustomModel,
    datetime_pd,
)


# Responses
class TagResponse(CustomModel):
    content_count: int
    name: str


class ArticleContentResponseBase(CustomModel):
    image: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    title_en: str | None
    title_ua: str | None
    slug: str


class ArticleAnimeContentResponse(ArticleContentResponseBase):
    data_type: Literal["anime"]
    title_ja: str | None


class ArticleMangaNovelContentResponse(ArticleContentResponseBase):
    data_type: Literal["manga", "novel"]
    title_original: str | None


# TODO: Make separate responses for catalog and article info
class ArticleResponse(CustomModel):
    data_type: Literal["article"]
    author: FollowUserResponse
    tags: list[TagResponse]
    created: datetime_pd
    updated: datetime_pd
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


class ArticlePreviewResponse(ArticleResponse):
    preview: list[dict]
