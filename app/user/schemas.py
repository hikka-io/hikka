from app.schemas import CustomModel, UserResponse
from pydantic import EmailStr, Field
from app.schemas import datetime_pd


# Responses
class ActivityResponse(CustomModel):
    timestamp: datetime_pd
    actions: int


class FavouriteStatsResponse(CustomModel):
    collection: int = 0
    character: int = 0
    anime: int = 0
    manga: int = 0
    novel: int = 0


class UserStatsResponse(CustomModel):
    favourites_count: FavouriteStatsResponse
    comments_count: int = 0
    reviews_count: int = 0
    edits_count: int = 0


class UserResponseFollowed(UserResponse):
    is_followed: bool


class UserWithEmailResponse(UserResponse):
    email: EmailStr | None = Field(description="User's email address")
