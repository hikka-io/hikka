from app.schemas import CustomModel
from pydantic import Field
from typing import Literal


# Responses
class PersonResponse(CustomModel):
    data_type: Literal["person"]
    name_native: str | None = Field(examples=["高橋 李依"])
    name_ua: str | None = Field(examples=["Ріє Такахаші"])
    name_en: str | None = Field(examples=["Rie Takahashi"])
    image: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    slug: str = Field(examples=["rie-takahashi-123456"])
    description_ua: str | None
    synonyms: list[str]


class RoleResponse(CustomModel):
    name_ua: str | None
    name_en: str | None
    weight: int | None
    slug: str


class ContentAuthorResponse(CustomModel):
    roles: list[RoleResponse]
    person: PersonResponse


class AnimeStaffResponse(ContentAuthorResponse):
    weight: int | None
