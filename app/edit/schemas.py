from pydantic import Field, field_validator
from app.schemas import datetime_pd
from app import constants
from enum import Enum

from app.schemas import (
    PaginationResponse,
    AnimeAgeRatingEnum,
    ContentStatusEnum,
    CharacterResponse,
    QuerySearchArgs,
    PersonResponse,
    AnimeMediaEnum,
    MangaMediaEnum,
    NovelMediaEnum,
    PaginationArgs,
    AnimeResponse,
    MangaResponse,
    NovelResponse,
    UserResponse,
    SeasonEnum,
    CustomModel
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


class AnimeTodoArgs(QuerySearchArgs, PaginationArgs):
    media_type: list[AnimeMediaEnum] = []
    mal_id: int | None = None

    fields: list[str] = []
    sort: list[str] = []
    season: list[SeasonEnum] = []
    status: list[ContentStatusEnum] = []
    rating: list[AnimeAgeRatingEnum] = []
    years: list[int | None] = Field(
        default=[None, None], min_length=2, max_length=2
    )
    genres: list[str] = []
    studios: list[str] = []

    @field_validator("fields")
    def validate_fields(cls, fields):
        valid_fields = [
            "title_ua",
            "title_en",
            "title_original",
            "synopsis_ua",
            "synopsis_en",
        ]

        stripped = [field[1:] if field.startswith("-") else field for field in fields]

        if len(stripped) != len(set(stripped)):
            raise ValueError("Invalid fields: duplicates")

        for field in stripped:
            if field not in valid_fields:
                raise ValueError(f"Invalid field value: {field}")

        return fields

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        valid_orders = ["asc", "desc"]
        valid_fields = [
            "title_ua",
            "title_en",
            "title_original",
            "start_date",
            "media_type",
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

    @field_validator("years")
    def validate_years(cls, years):
        if years[0] is not None and years[1] is not None and years[0] > years[1]:
            raise ValueError("The first year must be less than the second year.")

        return years


class MangaTodoArgs(QuerySearchArgs, PaginationArgs):
    media_type: list[MangaMediaEnum] = []
    mal_id: int | None = None

    fields: list[str] = []
    sort: list[str] = []
    status: list[ContentStatusEnum] = []
    years: list[int | None] = Field(
        default=[None, None], min_length=2, max_length=2
    )
    genres: list[str] = []
    magazines: list[str] = []

    @field_validator("fields")
    def validate_fields(cls, fields):
        valid_fields = [
            "title_ua",
            "title_en",
            "title_original",
            "synopsis_ua",
            "synopsis_en",
        ]

        stripped = [field[1:] if field.startswith("-") else field for field in fields]

        if len(stripped) != len(set(stripped)):
            raise ValueError("Invalid fields: duplicates")

        for field in stripped:
            if field not in valid_fields:
                raise ValueError(f"Invalid field value: {field}")

        return fields

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        valid_orders = ["asc", "desc"]
        valid_fields = [
            "title_ua",
            "title_en",
            "title_original",
            "start_date",
            "media_type",
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

    @field_validator("years")
    def validate_years(cls, years):
        if years[0] is not None and years[1] is not None and years[0] > years[1]:
            raise ValueError("The first year must be less than the second year.")

        return years


class NovelTodoArgs(QuerySearchArgs, PaginationArgs):
    media_type: list[NovelMediaEnum] = []
    mal_id: int | None = None

    fields: list[str] = []
    sort: list[str] = []
    status: list[ContentStatusEnum] = []
    years: list[int | None] = Field(
        default=[None, None], min_length=2, max_length=2
    )
    genres: list[str] = []
    magazines: list[str] = []

    @field_validator("fields")
    def validate_fields(cls, fields):
        valid_fields = [
            "title_ua",
            "title_en",
            "title_original",
            "synopsis_ua",
            "synopsis_en",
        ]

        stripped = [field[1:] if field.startswith("-") else field for field in fields]

        if len(stripped) != len(set(stripped)):
            raise ValueError("Invalid fields: duplicates")

        for field in stripped:
            if field not in valid_fields:
                raise ValueError(f"Invalid field value: {field}")

        return fields

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        valid_orders = ["asc", "desc"]
        valid_fields = [
            "title_ua",
            "title_en",
            "title_original",
            "start_date",
            "media_type",
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

    @field_validator("years")
    def validate_years(cls, years):
        if years[0] is not None and years[1] is not None and years[0] > years[1]:
            raise ValueError("The first year must be less than the second year.")

        return years


class CharacterTodoArgs(QuerySearchArgs, PaginationArgs):
    fields: list[str] = []
    sort: list[str] = []
    content_type: EditContentToDoEnum | None = None
    content_slug: str | None = None

    @field_validator("fields")
    def validate_fields(cls, fields):
        valid_fields = [
            "name_ua",
            "name_en",
            "name_original",
            "description_ua",
        ]

        stripped = [field[1:] if field.startswith("-") else field for field in fields]

        if len(stripped) != len(set(stripped)):
            raise ValueError("Invalid fields: duplicates")

        for field in stripped:
            if field not in valid_fields:
                raise ValueError(f"Invalid field value: {field}")

        return fields

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        valid_orders = ["asc", "desc"]
        valid_fields = ["name_ua", "name_en", "name_original"]

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


class PersonTodoArgs(QuerySearchArgs, PaginationArgs):
    fields: list[str] = []
    sort: list[str] = []
    content_type: EditContentToDoEnum | None = None
    content_slug: str | None = None

    @field_validator("fields")
    def validate_fields(cls, fields):
        valid_fields = [
            "name_ua",
            "name_en",
            "name_original",
        ]

        stripped = [field[1:] if field.startswith("-") else field for field in fields]

        if len(stripped) != len(set(stripped)):
            raise ValueError("Invalid fields: duplicates")

        for field in stripped:
            if field not in valid_fields:
                raise ValueError(f"Invalid field value: {field}")

        return fields

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        valid_orders = ["asc", "desc"]
        valid_fields = ["name_ua", "name_en", "name_original"]

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


class TodoContentIssuesInfo(CustomModel):
    title_ua_absent: bool
    title_en_absent: bool
    title_original_absent: bool
    synopsis_ua_absent: bool
    synopsis_en_absent: bool
    # Add more required fields for content: Anime, Manga, Novel
    # for example: image, link_to_content (orphan)...
    # Optional fields such as synonyms should not be present in this list


class TodoCharacterIssuesInfo(CustomModel):
    name_ua_absent: bool
    name_en_absent: bool
    name_original_absent: bool
    description_ua_absent: bool
    # Add more required fields for character


class TodoPersonIssuesInfo(CustomModel):
    name_ua_absent: bool
    name_en_absent: bool
    name_original_absent: bool
    # Add more required fields for peoples

class TodoAnimeResponse(CustomModel):
    item: AnimeResponse
    issues: TodoContentIssuesInfo

    @classmethod
    def from_(cls, anime) -> "TodoAnimeResponse":
        return cls(
            item=anime,
            issues=TodoContentIssuesInfo(
                title_ua_absent=anime.title_ua is None,
                title_en_absent=anime.title_en is None,
                title_original_absent=anime.title_ja is None,
                synopsis_ua_absent=anime.synopsis_ua is None,
                synopsis_en_absent=anime.synopsis_en is None,
            ),
        )


class TodoMangaResponse(CustomModel):
    item: MangaResponse
    issues: TodoContentIssuesInfo

    @classmethod
    def from_(cls, manga) -> "TodoMangaResponse":
        return cls(
            item=manga,
            issues=TodoContentIssuesInfo(
                title_ua_absent=manga.title_ua is None,
                title_en_absent=manga.title_en is None,
                title_original_absent=manga.title_original is None,
                synopsis_ua_absent=manga.synopsis_ua is None,
                synopsis_en_absent=manga.synopsis_en is None,
            ),
        )


class TodoNovelResponse(CustomModel):
    item: NovelResponse
    issues: TodoContentIssuesInfo

    @classmethod
    def from_(cls, novel) -> "TodoNovelResponse":
        return cls(
            item=novel,
            issues=TodoContentIssuesInfo(
                title_ua_absent=novel.title_ua is None,
                title_en_absent=novel.title_en is None,
                title_original_absent=novel.title_original is None,
                synopsis_ua_absent=novel.synopsis_ua is None,
                synopsis_en_absent=novel.synopsis_en is None,
            ),
        )


class TodoCharacterResponse(CustomModel):
    item: CharacterResponse
    issues: TodoCharacterIssuesInfo

    @classmethod
    def from_(cls, character) -> "TodoCharacterResponse":
        return cls(
            item=character,
            issues=TodoCharacterIssuesInfo(
                name_ua_absent=character.name_ua is None,
                name_en_absent=character.name_en is None,
                name_original_absent=character.name_ja is None,
                description_ua_absent=character.description_ua is None,
            ),
        )


class TodoPersonResponse(CustomModel):
    item: PersonResponse
    issues: TodoPersonIssuesInfo

    @classmethod
    def from_(cls, person) -> "TodoPersonResponse":
        return cls(
            item=person,
            issues=TodoPersonIssuesInfo(
                name_ua_absent=person.name_ua is None,
                name_en_absent=person.name_en is None,
                name_original_absent=person.name_native is None,
            ),
        )


class TodoAnimeListResponse(CustomModel):
    list: list[TodoAnimeResponse]
    pagination: PaginationResponse


class TodoMangaListResponse(CustomModel):
    list: list[TodoMangaResponse]
    pagination: PaginationResponse


class TodoNovelListResponse(CustomModel):
    list: list[TodoNovelResponse]
    pagination: PaginationResponse


class TodoCharacterListResponse(CustomModel):
    list: list[TodoCharacterResponse]
    pagination: PaginationResponse


class TodoPersonListResponse(CustomModel):
    list: list[TodoPersonResponse]
    pagination: PaginationResponse
