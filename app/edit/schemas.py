from datetime import datetime
from pydantic import Field
from app import constants
from typing import Union
from enum import Enum

from app.schemas import (
    PaginationResponse,
    ORJSONModel,
)


# Enums
class ContentTypeEnum(str, Enum):
    content_anime = constants.CONTENT_ANIME


class AnimeVideoTypeEnum(str, Enum):
    video_promo = constants.VIDEO_PROMO
    video_music = constants.VIDEO_MUSIC


class AnimeOSTTypeEnum(str, Enum):
    opening = constants.OST_OPENING
    ending = constants.OST_ENDING


class EditStatusEnum(str, Enum):
    edit_approved = constants.EDIT_APPROVED
    edit_pending = constants.EDIT_PENDING
    edit_denied = constants.EDIT_DENIED
    edit_closed = constants.EDIT_CLOSED


# Args
class EditArgs(ORJSONModel):
    description: Union[str, None] = Field(example="...", max_length=420)
    after: dict


class AnimeEditArgs(ORJSONModel):
    synopsis_en: Union[str, None] = Field(example="...")
    synopsis_ua: Union[str, None] = Field(example="...")
    synonyms: Union[list[str], None] = Field()

    title_ja: Union[str, None] = Field(
        example="Kimetsu no Yaiba: Mugen Ressha-hen", max_length=255
    )
    title_en: Union[str, None] = Field(
        example="Demon Slayer: Kimetsu no Yaiba Mugen Train Arc", max_length=255
    )
    title_ua: Union[str, None] = Field(
        example="Клинок, який знищує демонів: Арка Нескінченного потяга",
        max_length=255,
    )


# Response
# ToDo: make universal UserResponse
class UserResponse(ORJSONModel):
    username: str = Field(example="hikka")


class EditResponse(ORJSONModel):
    content_type: ContentTypeEnum = Field(example="anime")
    description: Union[str, None] = Field(example="...")
    status: EditStatusEnum = Field(example="pending")
    created: datetime = Field(example=1693850684)
    updated: datetime = Field(example=1693850684)
    moderator: Union[UserResponse, None]
    edit_id: int = Field(example=3)
    before: Union[dict, None]
    author: UserResponse
    after: dict
    slug: str


class EditListResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[EditResponse]
