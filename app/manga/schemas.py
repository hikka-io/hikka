from pydantic import Field
from app.schemas import datetime_pd

from app.schemas import (
    ContentAuthorResponse,
    MangaResponseWithRead,
    PaginationResponse,
    ReadStatsResponse,
    MagazineResponse,
    ExternalResponse,
    DataTypeMixin,
    GenreResponse,
    CustomModel,
)


# Responses
class MangaPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[MangaResponseWithRead]


class MangaInfoResponse(CustomModel, DataTypeMixin):
    authors: list[ContentAuthorResponse]
    magazines: list[MagazineResponse]
    external: list[ExternalResponse]
    start_date: datetime_pd | None = Field(examples=[786585600])
    end_date: datetime_pd | None = Field(examples=[1008806400])
    genres: list[GenreResponse]
    title_original: str | None = Field(examples=["Monster"])
    stats: ReadStatsResponse
    synopsis_en: str | None = Field(examples=["..."])
    synopsis_ua: str | None = Field(examples=["..."])
    media_type: str | None = Field(examples=["manga"])
    chapters: int | None = Field(examples=[162])
    title_en: str | None = Field(examples=["Monster"])
    title_ua: str | None = Field(examples=["Монстр"])
    updated: datetime_pd
    synonyms: list[str]
    comments_count: int
    has_franchise: bool = Field(examples=[True])
    translated_ua: bool = Field(examples=[True])
    volumes: int | None = Field(examples=[18])
    status: str | None = Field(examples=["finished"])
    image: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    year: int | None = Field(examples=[1994])
    scored_by: int = Field(examples=[99368])
    score: float = Field(examples=[9.16])
    mal_id: int = Field(examples=[1])
    nsfw: bool = Field(examples=[False])
    slug: str = Field(examples=["monster-54bb37"])
