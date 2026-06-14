from app.schemas import CustomModel
from typing import Literal


# Args
class ReviewArgs(CustomModel):
    recommended: Literal["yes", "no", "maybe"]
