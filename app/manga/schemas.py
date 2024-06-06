from pydantic import Field, field_validator
from app.schemas import datetime_pd
from pydantic import PositiveInt

from app.schemas import (
    ContentAuthorResponse,
    PaginationResponse,
    ContentStatusEnum,
    ReadStatsResponse,
    MagazineResponse,
    ExternalResponse,
    QuerySearchArgs,
    MangaMediaEnum,
    DataTypeMixin,
    GenreResponse,
    CustomModel,
)


# Args
class MangaSearchArgs(QuerySearchArgs):
    sort: list[str] = ["score:desc", "scored_by:desc"]
    genres: list[str] = []

    media_type: list[MangaMediaEnum] = []
    status: list[ContentStatusEnum] = []
    only_translated: bool = False
    magazines: list[str] = []

    years: list[PositiveInt | None] | None = Field(
        default=[None, None],
        examples=[[2000, 2020]],
    )

    score: list[int | None] = Field(
        default=[None, None],
        min_length=2,
        max_length=2,
        examples=[[0, 10]],
    )

    @field_validator("years")
    def validate_years(cls, years):
        if not years:
            return [None, None]

        if len(years) == 0:
            return [None, None]

        if len(years) != 2:
            raise ValueError("Lenght of years list must be 2.")

        if all(year is not None for year in years) and years[0] > years[1]:
            raise ValueError(
                "The first year must be less than the second year."
            )

        return years

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        valid_orders = ["asc", "desc"]
        valid_fields = [
            "media_type",
            "start_date",
            "scored_by",
            "score",
        ]

        if len(sort_list) != len(set(sort_list)):
            raise ValueError("Invalid sort: duplicates")

        for sort_item in sort_list:
            parts = sort_item.split(":")

            if len(parts) != 2:
                raise ValueError(f"Invalid sort format: {sort_item}")

            field, order = parts

            if field not in valid_fields or order not in valid_orders:
                raise ValueError(f"Invalid sort value: {sort_item}")

        return sort_list


# Responses
class MangaResponse(CustomModel, DataTypeMixin):
    title_original: str | None
    media_type: str | None
    title_ua: str | None
    title_en: str | None
    chapters: int | None
    volumes: int | None
    translated_ua: bool
    status: str | None
    image: str | None
    year: int | None
    scored_by: int
    score: float
    slug: str


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
