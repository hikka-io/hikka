from app.schemas import PaginationResponse
from pydantic import Field

from app.schemas import (
    FollowUserResponse,
    CustomModel,
)


# Responses
class FollowUserPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[FollowUserResponse]


class FollowStatsResponse(CustomModel):
    followers: int = Field(examples=[10])
    following: int = Field(examples=[3])


class FollowResponse(CustomModel):
    follow: bool = Field(examples=[True])
