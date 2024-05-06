from app.schemas import CustomModel
from app.schemas import datetime_pd


# Responses
class ActivityResponse(CustomModel):
    timestamp: datetime_pd
    actions: int
