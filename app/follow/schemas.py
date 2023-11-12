from app.schemas import PaginationResponse
from pydantic import Field

from app.schemas import (
    ORJSONModel,
    UserResponse,
)


# Responses
class UserPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[UserResponse]


class FollowStatsResponse(ORJSONModel):
    followers: int = Field(example=10)
    following: int = Field(example=3)


class FollowResponse(ORJSONModel):
    follow: bool = Field(example=True)
