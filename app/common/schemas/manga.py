from app.common.schemas.search import ReadSearchBaseMixin
from app.common.schemas.magazine import MagazineResponse
from app.common.schemas.read import ReadResponseBase
from app.common.schemas.genre import GenreResponse
from pydantic import field_validator
from typing import Literal
from app import constants
from enum import Enum


from app.schemas import (
    QuerySearchArgs,
    CustomModel,
    datetime_pd,
    YearsMixin,
)


# Enums
class MangaMediaEnum(str, Enum):
    one_shot = constants.MEDIA_TYPE_ONE_SHOT
    doujin = constants.MEDIA_TYPE_DOUJIN
    manhua = constants.MEDIA_TYPE_MANHUA
    manhwa = constants.MEDIA_TYPE_MANHWA
    manga = constants.MEDIA_TYPE_MANGA


# Args
class MangaSearchMediaTypeMixin:
    media_type: list[MangaMediaEnum] = []


class MangaSearchArgs(
    QuerySearchArgs,
    ReadSearchBaseMixin,
    MangaSearchMediaTypeMixin,
    YearsMixin,
):
    sort: list[str] = ["score:desc", "scored_by:desc"]

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        return utils.check_sort(
            sort_list,
            [
                "native_scored_by",
                "native_score",
                "media_type",
                "start_date",
                "scored_by",
                "created",
                "updated",
                "score",
            ],
        )

    @field_validator("score", "native_score")
    def validate_score(cls, scores):
        if all(score is not None for score in scores) and scores[0] > scores[1]:
            raise ValueError(
                "The first score must be less than the second score."
            )

        if scores[0] and scores[0] < 0:
            raise ValueError("Score can't be less than 0.")

        if scores[1] and scores[1] > 10:
            raise ValueError("Score can't be more than 10.")

        return scores


# Responses
class MangaResponse(CustomModel):
    data_type: Literal["manga"]
    start_date: datetime_pd | None
    end_date: datetime_pd | None
    created: datetime_pd | None
    updated: datetime_pd | None
    title_original: str | None
    title_native: str | None
    media_type: str | None
    native_scored_by: int
    title_ua: str | None
    title_en: str | None
    chapters: int | None
    volumes: int | None
    translated_ua: bool
    native_score: float
    status: str | None
    image: str | None
    year: int | None
    scored_by: int
    score: float
    mal_id: int
    slug: str

    magazines: list[MagazineResponse]
    genres: list[GenreResponse]
    synopsis_en: str | None
    synopsis_ua: str | None


class MangaResponseWithRead(MangaResponse):
    read: list[ReadResponseBase]
