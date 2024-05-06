from app.schemas import datetime_pd

from app.schemas import (
    PaginationResponse,
    AnimeResponse,
    UserResponse,
    CustomModel,
)


# Responses
class HistoryResponse(CustomModel):
    content: AnimeResponse | None = None
    created: datetime_pd
    updated: datetime_pd
    user: UserResponse
    history_type: str
    reference: str
    data: dict


class HistoryPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[HistoryResponse]
