from app.schemas import (
    AnimeFavouriteResponse,
    PaginationResponse,
    CustomModel,
)


# Responses
class AnimeFavouritePaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[AnimeFavouriteResponse]
