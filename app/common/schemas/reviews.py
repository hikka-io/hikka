from app.schemas import CustomModel
from typing import Literal

# Litterals
ReviewRecommended = Literal["yes", "no", "maybe"]


# Args
class ReviewArgs(CustomModel):
    recommended: ReviewRecommended


# Responses
class ReviewResponse(CustomModel):
    recommended: str
