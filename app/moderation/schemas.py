from app.schemas import PaginationResponse, CustomModel
from app.schemas import datetime_pd


# Responses
class ModerationResponse(CustomModel):
    target_type: str
    created: datetime_pd
    reference: str
    data: dict


class ModerationPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[ModerationResponse]
