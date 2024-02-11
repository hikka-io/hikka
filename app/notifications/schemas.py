from datetime import datetime

from app.schemas import (
    PaginationResponse,
    UserResponse,
    CustomModel,
)


# Responses
class SimpleEditResponse(CustomModel):
    edit_id: int


class SimpleCommentResponse(CustomModel):
    author: UserResponse
    text: str | None
    reference: str
    depth: int


class NotificationResponse(CustomModel):
    content: SimpleCommentResponse | SimpleEditResponse | None = None
    notification_type: str
    created: datetime
    updated: datetime
    reference: str


class NotificationPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[NotificationResponse]
