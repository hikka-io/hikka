from app.schemas import ORJSONModel
from datetime import datetime
from pydantic import Field


# Args
class DescriptionArgs(ORJSONModel):
    description: str | None = Field(
        default=None, max_length=140, example="Hikka"
    )


# Responses
class UserResponse(ORJSONModel):
    description: str | None = Field(example="Hikka")
    created: datetime = Field(example=1686088809)
    username: str = Field(example="hikka")
    avatar: str
