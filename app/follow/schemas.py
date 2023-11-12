from app.schemas import PaginationResponse
from pydantic import Field

from app.schemas import (
    CustomModel,
    UserResponse,
)


# Responses
class UserPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[UserResponse]


class FollowStatsResponse(CustomModel):
    followers: int = Field(example=10)
    following: int = Field(example=3)


class FollowResponse(CustomModel):
    follow: bool = Field(example=True)
