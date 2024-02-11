from app.schemas import PaginationResponse, CustomModel
from datetime import datetime


# Responses
class NotificationResponse(CustomModel):
    notification_type: str
    created: datetime
    reference: str
    seen: bool
    data: dict


class NotificationPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[NotificationResponse]
