from app.schemas import PaginationResponse
from app.schemas import ORJSONModel
from datetime import datetime
from pydantic import Field
from typing import Union


# Args
class DescriptionArgs(ORJSONModel):
    description: Union[str, None] = Field(default=None, max_length=140)


# Responses
class UserResponse(ORJSONModel):
    description: Union[str, None]
    created: datetime
    reference: str
    username: str


class WatchStatsResponse(ORJSONModel):
    completed: int
    watching: int
    planned: int
    dropped: int
    on_hold: int


class UserPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[UserResponse]
