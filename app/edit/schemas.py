from pydantic import Field, field_validator
from app.schemas import datetime_pd
from app import constants
from enum import Enum

from app.schemas import (
    PaginationResponse,
    CharacterResponse,
    PersonResponse,
    AnimeResponse,
    MangaResponse,
    NovelResponse,
    UserResponse,
    CustomModel,
)


# Enums
class ContentToDoEnum(str, Enum):
    synopsis_ua = constants.TODO_SYNOPSIS_UA
    title_ua = constants.TODO_TITLE_UA


class EditContentToDoEnum(str, Enum):
    content_anime = constants.CONTENT_ANIME
    content_manga = constants.CONTENT_MANGA
    content_novel = constants.CONTENT_NOVEL


class EditContentTypeEnum(str, Enum):
    content_character = constants.CONTENT_CHARACTER
    content_person = constants.CONTENT_PERSON
    content_anime = constants.CONTENT_ANIME
    content_manga = constants.CONTENT_MANGA
    content_novel = constants.CONTENT_NOVEL


class EditStatusEnum(str, Enum):
    edit_accepted = constants.EDIT_ACCEPTED
    edit_pending = constants.EDIT_PENDING
    edit_denied = constants.EDIT_DENIED
    edit_closed = constants.EDIT_CLOSED


# Args
class EditSearchArgs(CustomModel):
    sort: list[str] = ["edit_id:desc", "created:desc"]
    content_type: EditContentTypeEnum | None = None
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
    description: str | None = Field(None, examples=["..."], max_length=2048)
    auto: bool = Field(default=False)
    after: dict

    @field_validator("after")
    def validate_after(cls, after):
        if after == {}:
            raise ValueError("After field can't be empty")

        return after

    @field_validator("description")
    def validate_description(cls, description):
        return description.strip("\n") if description else description


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


class MangaEditArgs(CustomModel):
    synopsis_en: str | None = Field(None, examples=["..."])
    synopsis_ua: str | None = Field(None, examples=["..."])
    synonyms: list[str] | None = None
    title_original: str | None = None
    title_en: str | None = None
    title_ua: str | None = None


class NovelEditArgs(CustomModel):
    synopsis_en: str | None = Field(None, examples=["..."])
    synopsis_ua: str | None = Field(None, examples=["..."])
    synonyms: list[str] | None = None
    title_original: str | None = None
    title_en: str | None = None
    title_ua: str | None = None


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
class EditResponseBase(CustomModel):
    content_type: EditContentTypeEnum = Field(examples=["anime"])
    status: EditStatusEnum = Field(examples=["pending"])
    created: datetime_pd = Field(examples=[1693850684])
    updated: datetime_pd = Field(examples=[1693850684])
    description: str | None = Field(examples=["..."])
    edit_id: int = Field(examples=[3])
    moderator: UserResponse | None
    author: UserResponse | None
    before: dict | None
    system_edit: bool
    after: dict


class EditResponse(EditResponseBase):
    # TODO: maybe we should use Pydantic's discriminator here?
    content: (
        AnimeResponse
        | MangaResponse
        | NovelResponse
        | PersonResponse
        | CharacterResponse
    )

    comments_count: int
    reference: str


class EditSimpleResponse(EditResponseBase):
    content: dict = Field(validation_alias="content_preview")


class EditListResponse(CustomModel):
    pagination: PaginationResponse
    list: list[EditSimpleResponse]
