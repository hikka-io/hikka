from app.schemas import PaginationResponse
from pydantic import BaseModel, Field
from ..utils import Datetime
from typing import Union


# Args
class DescriptionArgs(BaseModel):
    description: Union[str, None] = Field(default=None, max_length=140)


# Responses
class UserResponse(BaseModel):
    description: Union[str, None]
    created: Datetime
    reference: str
    username: str


class WatchStatsResponse(BaseModel):
    completed: int
    watching: int
    planned: int
    dropped: int
    on_hold: int


class UserPaginationResponse(BaseModel):
    pagination: PaginationResponse
    list: list[UserResponse]


class FollowStatsResponse(BaseModel):
    followers: int
    following: int
