from pydantic import Field, field_validator
from datetime import datetime
from app import constants
from enum import Enum

from app.schemas import (
    PaginationResponse,
    PersonResponse,
    AnimeResponse,
    UserResponse,
    CustomModel,
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
class EditArgs(CustomModel):
    description: str | None = Field(None, examples=["..."], max_length=420)
    after: dict

    @field_validator("after")
    def validate_after(cls, after):
        if after == {}:
            raise ValueError("After field can't be empty")

        return after


class AnimeEditArgs(CustomModel):
    synopsis_en: str | None = Field(None, examples=["..."])
    synopsis_ua: str | None = Field(None, examples=["..."])
    synonyms: list[str] | None = None

    title_ja: str | None = Field(
        None,
        examples=["Kimetsu no Yaiba: Mugen Ressha-hen"],
        max_length=255,
    )

    title_en: str | None = Field(
        None,
        examples=["Demon Slayer: Kimetsu no Yaiba Mugen Train Arc"],
        max_length=255,
    )

    title_ua: str | None = Field(
        None,
        examples=["Клинок, який знищує демонів: Арка Нескінченного потяга"],
        max_length=255,
    )


class PersonEditArgs(CustomModel):
    name_native: str | None = Field(None, examples=["丸山 博雄"], max_length=255)
    name_ua: str | None = Field(None, examples=["Хіро Маруяма"], max_length=255)
    name_en: str | None = Field(
        None, examples=["Hiroo Maruyama"], max_length=255
    )


# Response
class EditResponse(CustomModel):
    content_type: ContentTypeEnum = Field(examples=["anime"])
    status: EditStatusEnum = Field(examples=["pending"])
    description: str | None = Field(examples=["..."])
    created: datetime = Field(examples=[1693850684])
    updated: datetime = Field(examples=[1693850684])
    edit_id: int = Field(examples=[3])
    moderator: UserResponse | None
    author: UserResponse | None
    before: dict | None
    system_edit: bool
    after: dict

    # ToDo: maybe we should use Pydantic's discriminator here?
    content: AnimeResponse | PersonResponse


class EditListResponse(CustomModel):
    pagination: PaginationResponse
    list: list[EditResponse]
