from datetime import datetime

from app.schemas import (
    PaginationResponse,
    AnimeResponse,
    CustomModel,
)


# Responses
class HistoryResponse(CustomModel):
    content: AnimeResponse
    history_type: str
    created: datetime
    updated: datetime
    data: dict


class HistoryPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[HistoryResponse]
