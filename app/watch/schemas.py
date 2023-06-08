from app.schemas import ORJSONModel, WatchStatusEnum
from pydantic import Field
from typing import Union


# Args
class WatchArgs(ORJSONModel):
    note: Union[str, None] = Field(default=None, example="🤯")
    score: int = Field(default=0, ge=0, le=10, example=8)
    episodes: int = Field(default=0, ge=0, example=3)
    status: WatchStatusEnum
