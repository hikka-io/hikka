from app.schemas import CustomModel, PaginationResponse
from app.common.schemas.user import FollowUserResponse
from pydantic import Field


# Responses
class FollowUserPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[FollowUserResponse]


class FollowStatsResponse(CustomModel):
    followers: int = Field(examples=[10])
    following: int = Field(examples=[3])


class FollowResponse(CustomModel):
    follow: bool = Field(examples=[True])
