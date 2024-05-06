from app.schemas import PaginationResponse, CustomModel
from app.schemas import datetime_pd


# Responses
class NotificationResponse(CustomModel):
    notification_type: str
    created: datetime_pd
    reference: str
    seen: bool
    data: dict


class NotificationPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[NotificationResponse]


class NotificationUnseenResponse(CustomModel):
    unseen: int
