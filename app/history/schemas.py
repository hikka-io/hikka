from datetime import datetime

from app.schemas import (
    PaginationResponse,
    AnimeResponse,
    UserResponse,
    CustomModel,
)


# Responses
class HistoryResponse(CustomModel):
    content: AnimeResponse | None = None
    user: UserResponse
    history_type: str
    created: datetime
    updated: datetime
    reference: str
    data: dict


class HistoryPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[HistoryResponse]
