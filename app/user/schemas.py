from app.schemas import ORJSONModel
from pydantic import Field


# Args
class DescriptionArgs(ORJSONModel):
    description: str | None = Field(
        default=None, max_length=140, example="Hikka"
    )
