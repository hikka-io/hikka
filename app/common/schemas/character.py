from app.schemas import CustomModel, PaginationResponse
from pydantic import Field
from typing import Literal


# Responses
class CharacterResponse(CustomModel):
    data_type: Literal["character"]
    name_ua: str | None = Field(examples=["Меґумін"])
    name_en: str | None = Field(examples=["Megumin"])
    name_ja: str | None = Field(examples=["めぐみん"])
    image: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    slug: str = Field(examples=["megumin-123456"])
    synonyms: list[str]


class ContentCharacterResponse(CustomModel):
    main: bool = Field(examples=[True])
    character: CharacterResponse


class ContentCharacterPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[ContentCharacterResponse]
