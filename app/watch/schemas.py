from app.schemas import ORJSONModel, WatchStatusEnum
from pydantic import Field
from typing import Union


# Args
class WatchArgs(ORJSONModel):
    score: int = Field(default=0, ge=0, le=10)
    episodes: int = Field(default=0, ge=0)
    note: Union[str, None] = None
    status: WatchStatusEnum
