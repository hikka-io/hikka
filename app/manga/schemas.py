from app.schemas import datetime_pd

from app.schemas import (
    ContentAuthorResponse,
    PaginationResponse,
    ReadStatsResponse,
    MagazineResponse,
    ExternalResponse,
    DataTypeMixin,
    GenreResponse,
    MangaResponse,
    CustomModel,
)


# Responses
class MangaPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[MangaResponse]


class MangaInfoResponse(CustomModel, DataTypeMixin):
    authors: list[ContentAuthorResponse]
    magazines: list[MagazineResponse]
    external: list[ExternalResponse]
    start_date: datetime_pd | None
    end_date: datetime_pd | None
    genres: list[GenreResponse]
    title_original: str | None
    stats: ReadStatsResponse
    synopsis_en: str | None
    synopsis_ua: str | None
    media_type: str | None
    chapters: int | None
    title_en: str | None
    title_ua: str | None
    updated: datetime_pd
    synonyms: list[str]
    comments_count: int
    has_franchise: bool
    translated_ua: bool
    volumes: int | None
    status: str | None
    image: str | None
    year: int | None
    scored_by: int
    score: float
    mal_id: int
    nsfw: bool
    slug: str
