from pydantic import Field, validator
from datetime import datetime
from app import constants
from enum import Enum

from app.schemas import (
    PaginationResponse,
    UserResponse,
    ORJSONModel,
)


# Enums
class ContentTypeEnum(str, Enum):
    content_person = constants.CONTENT_PERSON
    content_anime = constants.CONTENT_ANIME


class AnimeVideoTypeEnum(str, Enum):
    video_promo = constants.VIDEO_PROMO
    video_music = constants.VIDEO_MUSIC


class AnimeOSTTypeEnum(str, Enum):
    opening = constants.OST_OPENING
    ending = constants.OST_ENDING


class EditStatusEnum(str, Enum):
    edit_accepted = constants.EDIT_ACCEPTED
    edit_pending = constants.EDIT_PENDING
    edit_denied = constants.EDIT_DENIED
    edit_closed = constants.EDIT_CLOSED


# Args
class EditArgs(ORJSONModel):
    description: str | None = Field(example="...", max_length=420)
    after: dict

    @validator("after")
    def validate_after(cls, after):
        if after == {}:
            raise ValueError("After field can't be empty")

        return after


class AnimeEditArgs(ORJSONModel):
    synopsis_en: str | None = Field(example="...")
    synopsis_ua: str | None = Field(example="...")
    synonyms: list[str] | None = Field()

    title_ja: str | None = Field(
        example="Kimetsu no Yaiba: Mugen Ressha-hen",
        max_length=255,
    )
    title_en: str | None = Field(
        example="Demon Slayer: Kimetsu no Yaiba Mugen Train Arc",
        max_length=255,
    )
    title_ua: str | None = Field(
        example="Клинок, який знищує демонів: Арка Нескінченного потяга",
        max_length=255,
    )


class PersonEditArgs(ORJSONModel):
    name_native: str | None = Field(example="丸山 博雄", max_length=255)
    name_en: str | None = Field(example="Hiroo Maruyama", max_length=255)
    name_ua: str | None = Field(example="Хіро Маруяма", max_length=255)


# Response
class ContentSlugResponse(ORJSONModel):
    slug: str


class EditResponse(ORJSONModel):
    content_type: ContentTypeEnum = Field(example="anime")
    status: EditStatusEnum = Field(example="pending")
    description: str | None = Field(example="...")
    created: datetime = Field(example=1693850684)
    updated: datetime = Field(example=1693850684)
    moderator: UserResponse | None
    edit_id: int = Field(example=3)
    author: UserResponse
    before: dict | None
    after: dict

    # ToDo: find better way to do that
    content: ContentSlugResponse


class EditListResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[EditResponse]
