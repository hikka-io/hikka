from app.schemas import CustomModel
from datetime import datetime


# Responses
class ActivityResponse(CustomModel):
    timestamp: datetime
    actions: int
