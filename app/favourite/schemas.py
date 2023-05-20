from app.schemas import ORJSONModel
from datetime import datetime


# Responses
class FavouriteResponse(ORJSONModel):
    created: datetime


class DeleteResponse(ORJSONModel):
    success: bool
