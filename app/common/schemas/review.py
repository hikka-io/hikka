from app.schemas import CustomModel
from pydantic import Field


class ReviewStatsResponse(CustomModel):
    maybe: int = Field(examples=[1337], default=0)
    yes: int = Field(examples=[8801], default=0)
    no: int = Field(examples=[404], default=0)
