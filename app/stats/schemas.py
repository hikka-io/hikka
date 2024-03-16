from app.schemas import PaginationResponse, CustomModel, UserResponse


# Responses
class EditsTopResponse(CustomModel):
    user: UserResponse
    accepted: int
    closed: int
    denied: int


class EditsTopPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[EditsTopResponse]
