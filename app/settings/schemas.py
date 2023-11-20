from app.schemas import CustomModel
from pydantic import Field


# Args
class DescriptionArgs(CustomModel):
    description: str | None = Field(
        default=None, max_length=140, examples=["Hikka"]
    )
