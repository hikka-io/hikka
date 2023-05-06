from app.schemas import PaginationResponse
from pydantic import BaseModel
from ..utils import Datetime
from typing import Union


# Responses
class UserResponse(BaseModel):
    description: Union[str, None]
    created: Datetime
    reference: str
    username: str


class UserPaginationResponse(BaseModel):
    pagination: PaginationResponse
    list: list[UserResponse]


class FollowStatsResponse(BaseModel):
    followers: int
    following: int


class FollowResponse(BaseModel):
    follow: bool
