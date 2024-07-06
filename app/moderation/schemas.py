from app.edit.schemas import EditResponse
from app.schemas import datetime_pd

from app.schemas import (
    PaginationResponse,
    UserResponse,
    CustomModel,
)


# Responses
class ModerationResponse(CustomModel):
    content: EditResponse | None = None
    created: datetime_pd
    user: UserResponse
    history_type: str
    reference: str
    data: dict


class ModerationPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[ModerationResponse]
