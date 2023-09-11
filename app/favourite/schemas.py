from app.schemas import (
    AnimeFavouriteResponse,
    PaginationResponse,
    ORJSONModel,
)


# Responses
class AnimeFavouritePaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[AnimeFavouriteResponse]
