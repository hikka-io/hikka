from app.schemas import PaginationResponse, CustomModel
from app.common.schemas.user import UserResponse


# Responses
class EditsTopResponse(CustomModel):
    user: UserResponse
    accepted: int
    closed: int
    denied: int


class EditsTopPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[EditsTopResponse]
