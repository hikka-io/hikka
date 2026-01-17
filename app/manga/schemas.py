from pydantic import Field
from pydantic import field_validator
from app.schemas import datetime_pd
from app import constants

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
    start_date: datetime_pd | None
    end_date: datetime_pd | None
    genres: list[GenreResponse]
    title_original: str | None
    stats: ReadStatsResponse
    synopsis_en: str | None
    synopsis_ua: str | None
    media_type: str | None
    native_scored_by: int
    chapters: int | None
    title_en: str | None
    title_ua: str | None
    updated: datetime_pd
    synonyms: list[str]
    comments_count: int
    has_franchise: bool
    translated_ua: bool
    native_score: float
    volumes: int | None
    status: str | None
    image: str | None
    year: int | None
    scored_by: int
    score: float
    mal_id: int
    nsfw: bool
    slug: str

    @field_validator("external")
    def external_ordering(cls, value):
        def read_sort(item):
            order = {"Dengeki": 0}
            return order.get(item.text, 2)

        def reorder_read(input_list):
            return sorted(input_list, key=read_sort)

        general = []
        read = []

        for entry in value:
            if entry.type == constants.EXTERNAL_GENERAL:
                general.append(entry)

            if entry.type == constants.EXTERNAL_READ:
                read.append(entry)

        return general + reorder_read(read)
