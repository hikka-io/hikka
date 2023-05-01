from ..responses import PaginationResponse
from pydantic import BaseModel, Field
from ..utils import Datetime
from typing import Union

class UserResponse(BaseModel):
    reference: str = Field(example="684f4fca-f901-42b1-8531-b7d5146b15cc")
    description: Union[str, None] = Field(example="Опис користувача")
    created: Datetime = Field(example=1659279188)
    username: str = Field(example="user")

class WatchStatsResponse(BaseModel):
    completed: int = Field(example=479)
    watching: int = Field(example=51)
    planned: int = Field(example=87)
    dropped: int = Field(example=1)
    on_hold: int = Field(example=0)

class UserPaginationResponse(BaseModel):
    pagination: PaginationResponse
    list: list[UserResponse]

class FollowStatsResponse(BaseModel):
    followers: int = Field(example=10)
    following: int = Field(example=3)
