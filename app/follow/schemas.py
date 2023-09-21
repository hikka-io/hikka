from app.schemas import PaginationResponse
from app.schemas import ORJSONModel
from pydantic import Field


# Responses
class UserResponse(ORJSONModel):
    reference: str = Field(example="c773d0bf-1c42-4c18-aec8-1bdd8cb0a434")
    username: str = Field(example="hikka")
    avatar: str


class UserPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[UserResponse]


class FollowStatsResponse(ORJSONModel):
    followers: int = Field(example=10)
    following: int = Field(example=3)


class FollowResponse(ORJSONModel):
    follow: bool = Field(example=True)
