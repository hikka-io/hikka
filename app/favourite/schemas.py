from app.schemas import (
    AnimeFavouriteResponseWithWatch,
    PaginationResponse,
    CustomModel,
)


# Responses
class AnimeFavouritePaginationResponse(CustomModel):
    list: list[AnimeFavouriteResponseWithWatch]
    pagination: PaginationResponse
