from datetime import datetime, timedelta
from pydantic import field_validator

from app.schemas import (
    AnimeResponseWithWatch,
    PaginationResponse,
    AnimeStatusEnum,
    CustomModel,
    SeasonEnum,
)


# Args
class AnimeScheduleArgs(CustomModel):
    airing_season: list[SeasonEnum | int] | None = None
    status: AnimeStatusEnum | None = None

    @field_validator("airing_season")
    def validate_airing_season(cls, airing_season):
        if airing_season:
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
class AnimeScheduleResponse(CustomModel):
    anime: AnimeResponseWithWatch
    time_left: timedelta
    airing_at: datetime
    episode: int


class AnimeScheduleResponsePaginationResponse(CustomModel):
    list: list[AnimeScheduleResponse]
    pagination: PaginationResponse
