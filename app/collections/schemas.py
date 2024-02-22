from app.schemas import CustomModel
from pydantic import Field
from app import constants
from enum import Enum


# Enums
class ContentTypeEnum(str, Enum):
    content_character = constants.CONTENT_CHARACTER
    content_person = constants.CONTENT_PERSON
    content_anime = constants.CONTENT_ANIME


# Args
class CollectionContentArgs(CustomModel):
    comment: str | None = None
    label: str | None = None
    order: int
    slug: str


class CollectionArgs(CustomModel):
    content: list[CollectionContentArgs] = Field(max_length=500)
    title: str = Field(min_length=3, max_length=255)
    content_type: ContentTypeEnum
    description: str | None
    labels: list[str]
