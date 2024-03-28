from datetime import datetime, timedelta

from app.schemas import (
    AnimeResponseWithWatch,
    PaginationResponse,
    CustomModel,
)


# Responses
class AnimeScheduleResponse(CustomModel):
    anime: AnimeResponseWithWatch
    time_left: timedelta
    airing_at: datetime
    episode: int


class AnimeScheduleResponsePaginationResponse(CustomModel):
    list: list[AnimeScheduleResponse]
    pagination: PaginationResponse
