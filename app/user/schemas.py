from app.schemas import ORJSONModel
from datetime import datetime
from pydantic import Field
from typing import Union


# Args
class DescriptionArgs(ORJSONModel):
    description: Union[str, None] = Field(
        default=None, max_length=140, example="Hikka"
    )


# Responses
class UserResponse(ORJSONModel):
    description: Union[str, None] = Field(example="Hikka")
    created: datetime = Field(example=1686088809)
    username: str = Field(example="hikka")
