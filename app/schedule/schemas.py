from app.schemas import datetime_pd, timedelta_pd
from pydantic import field_validator

from app.schemas import (
    AnimeResponseWithWatch,
    AnimeAgeRatingEnum,
    PaginationResponse,
    AnimeStatusEnum,
    CustomModel,
    SeasonEnum,
)


# Args
class AnimeScheduleArgs(CustomModel):
    airing_season: list[SeasonEnum | int] | None = None
    rating: list[AnimeAgeRatingEnum] = []
    status: list[AnimeStatusEnum] = []
    only_watch: bool = False

    @field_validator("airing_season")
    def validate_airing_season(cls, airing_season):
        if not airing_season:
            return airing_season

        if len(airing_season) != 2:
            raise ValueError("Invalid airing season")

        if SeasonEnum(airing_season[0]) not in SeasonEnum:
            raise ValueError("Please specify valid season")

        if not isinstance(airing_season[1], int):
            raise ValueError("Please specify valid season")

        if airing_season[1] < 2020:
            raise ValueError("Please specify year beyond 2020")

        return airing_season


# Responses
class AnimeResponseWithSynopsis(AnimeResponseWithWatch):
    synopsis_en: str | None
    synopsis_ua: str | None


class AnimeScheduleResponse(CustomModel):
    anime: AnimeResponseWithSynopsis
    time_left: timedelta_pd
    airing_at: datetime_pd
    episode: int


class AnimeScheduleResponsePaginationResponse(CustomModel):
    list: list[AnimeScheduleResponse]
    pagination: PaginationResponse
