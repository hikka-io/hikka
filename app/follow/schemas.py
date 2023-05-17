from app.schemas import PaginationResponse
from app.schemas import ORJSONModel


# Responses
class UserResponse(ORJSONModel):
    reference: str
    username: str


class UserPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[UserResponse]


class FollowStatsResponse(ORJSONModel):
    followers: int
    following: int


class FollowResponse(ORJSONModel):
    follow: bool
