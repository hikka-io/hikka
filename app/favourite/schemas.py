from pydantic import BaseModel
from ..utils import Datetime


# Responses
class FavouriteResponse(BaseModel):
    created: Datetime


class DeleteResponse(BaseModel):
    success: bool
