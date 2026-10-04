from app.schemas import CustomModel
from pydantic import Field


# Responses
class GenreResponse(CustomModel):
    name_ua: str | None = Field(examples=["Комедія"])
    name_en: str | None = Field(examples=["Comedy"])
    slug: str = Field(examples=["comedy"])
    type: str = Field(examples=["genre"])


class GenreListResponse(CustomModel):
    list: list[GenreResponse]
