from pydantic import BaseModel, Field
from ..utils import Datetime

class FavouriteResponse(BaseModel):
    created: Datetime

class DeleteResponse(BaseModel):
    success: bool
