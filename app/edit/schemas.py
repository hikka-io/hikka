from pydantic import Field, field_validator
from datetime import datetime
from app import constants
from enum import Enum

from app.schemas import (
    PaginationResponse,
    CharacterResponse,
    PersonResponse,
    AnimeResponse,
    UserResponse,
    CustomModel,
)


# Enums
class AnimeToDoEnum(str, Enum):
    synopsis_ua = constants.TODO_ANIME_SYNOPSIS_UA
    title_ua = constants.TODO_ANIME_TITLE_UA


class ContentTypeEnum(str, Enum):
    content_character = constants.CONTENT_CHARACTER
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
class EditSearchArgs(CustomModel):
    sort: list[str] = ["edit_id:desc", "created:desc"]
    content_type: ContentTypeEnum | None = None
    status: EditStatusEnum | None = None
    moderator: str | None = None
    author: str | None = None
    slug: str | None = None

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        valid_orders = ["asc", "desc"]
        valid_fields = [
            "edit_id",
            "created",
        ]

        if len(sort_list) != len(set(sort_list)):
            raise ValueError("Invalid sort: duplicates")

        for sort_item in sort_list:
            parts = sort_item.split(":")

            if len(parts) != 2:
                raise ValueError(f"Invalid sort format: {sort_item}")

            field, order = parts

            if field not in valid_fields or order not in valid_orders:
                raise ValueError(f"Invalid sort value: {sort_item}")

        return sort_list


class EditArgs(CustomModel):
    description: str | None = Field(None, examples=["..."], max_length=420)
    auto: bool = Field(default=False)
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
    description_ua: str | None = Field(None, examples=["..."])
    name_native: str | None = Field(
        None, examples=["丸山 博雄"], max_length=255
    )
    name_ua: str | None = Field(None, examples=["Хіро Маруяма"], max_length=255)
    name_en: str | None = Field(
        None, examples=["Hiroo Maruyama"], max_length=255
    )
    synonyms: list[str] | None = None


class CharacterEditArgs(CustomModel):
    name_ja: str | None = Field(None, examples=["ガッツ"], max_length=255)
    name_ua: str | None = Field(None, examples=["Ґатс"], max_length=255)
    name_en: str | None = Field(None, examples=["Guts"], max_length=255)
    description_ua: str | None = Field(None, examples=["..."])
    synonyms: list[str] | None = None


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
    content: AnimeResponse | PersonResponse | CharacterResponse

    comments_count: int | None

    @field_validator("comments_count")
    def validate_after(cls, comments_count):
        if not comments_count:
            comments_count = 0

        return comments_count


class EditListResponse(CustomModel):
    pagination: PaginationResponse
    list: list[EditResponse]
