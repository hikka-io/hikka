from pydantic import Field, field_validator
from app.schemas import datetime_pd
from app import constants

from app.schemas import (
    AnimeExternalResponse,
    AnimeSearchArgsBase,
    AnimeVideoResponse,
    AnimeStaffResponse,
    PaginationResponse,
    CharacterResponse,
    CompanyTypeEnum,
    CompanyResponse,
    QuerySearchArgs,
    DataTypeMixin,
    CustomModel,
)


# Args
class AnimeSearchArgs(QuerySearchArgs, AnimeSearchArgsBase):
    sort: list[str] = ["score:desc", "scored_by:desc"]

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        valid_orders = ["asc", "desc"]
        valid_fields = [
            "media_type",
            "start_date",
            "scored_by",
            "score",
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


# Responses
class AnimeEpisodeResponse(CustomModel):
    aired: datetime_pd | None = Field(examples=[1686088809])
    title_ua: str | None = Field(
        examples=["Самопроголошена богиня і переродження в паралельному світі!"]
    )
    title_en: str | None = Field(
        examples=[
            "This Self-Proclaimed Goddess and Reincarnation in Another World!"
        ]
    )
    title_ja: str | None = Field(
        examples=["Kono Jishou Megami to Isekai Tenshou wo!"]
    )
    index: int = Field(examples=[1])


class AnimeEpisodesListResponse(CustomModel):
    pagination: PaginationResponse
    list: list[AnimeEpisodeResponse]


class AnimeCharacterResponse(CustomModel):
    main: bool = Field(examples=[True])
    character: CharacterResponse


class GenreResponse(CustomModel):
    name_ua: str | None = Field(examples=["Комедія"])
    name_en: str | None = Field(examples=["Comedy"])
    slug: str = Field(examples=["comedy"])
    type: str = Field(examples=["genre"])


class GenreListResposne(CustomModel):
    list: list[GenreResponse]


class AnimeCompanyResponse(CustomModel):
    company: CompanyResponse
    type: CompanyTypeEnum


class AnimeCharacterPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[AnimeCharacterResponse]


class AnimeStaffPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[AnimeStaffResponse]


class AnimeStatsResponse(CustomModel):
    completed: int = Field(examples=[1502335], default=0)
    watching: int = Field(examples=[83106], default=0)
    planned: int = Field(examples=[206073], default=0)
    dropped: int = Field(examples=[33676], default=0)
    on_hold: int = Field(examples=[30222], default=0)
    score_1: int = Field(examples=[3087], default=0)
    score_2: int = Field(examples=[2633], default=0)
    score_3: int = Field(examples=[4583], default=0)
    score_4: int = Field(examples=[11343], default=0)
    score_5: int = Field(examples=[26509], default=0)
    score_6: int = Field(examples=[68501], default=0)
    score_7: int = Field(examples=[211113], default=0)
    score_8: int = Field(examples=[398095], default=0)
    score_9: int = Field(examples=[298198], default=0)
    score_10: int = Field(examples=[184038], default=0)


class AnimeOSTResponse(CustomModel):
    index: int = Field(examples=[1])
    title: str | None = Field(examples=["fantastic dreamer"])
    author: str | None = Field(examples=["Machico"])
    spotify: str | None = Field(
        examples=["https://open.spotify.com/track/3BIhcWQV2hGRoEXdLL3Fzw"]
    )
    ost_type: str = Field(examples=["opening"])


class AnimeInfoResponse(CustomModel, DataTypeMixin):
    companies: list[AnimeCompanyResponse]
    genres: list[GenreResponse]

    start_date: datetime_pd | None = Field(examples=[1686088809])
    end_date: datetime_pd | None = Field(examples=[1686088809])
    updated: datetime_pd
    comments_count: int

    episodes_released: int | None = Field(examples=[10])
    episodes_total: int | None = Field(examples=[10])
    synopsis_en: str | None = Field(examples=["..."])
    synopsis_ua: str | None = Field(examples=["..."])
    media_type: str | None = Field(examples=["tv"])
    title_ua: str | None = Field(
        examples=["Цей прекрасний світ, благословенний Богом!"]
    )
    title_en: str | None = Field(
        examples=["KonoSuba: God's Blessing on This Wonderful World!"]
    )
    title_ja: str | None = Field(
        examples=["Kono Subarashii Sekai ni Shukufuku wo!"]
    )
    duration: int | None = Field(examples=[23])
    poster: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    status: str | None = Field(examples=["finished"])
    source: str | None = Field(examples=["light_novel"])
    rating: str | None = Field(examples=["pg_13"])
    has_franchise: bool = Field(examples=[True])
    scored_by: int = Field(examples=[1210150])
    score: float = Field(examples=[8.11])
    nsfw: bool = Field(examples=[False])
    slug: str = Field(examples=["kono-subarashii-sekai-ni-shukufuku-wo-123456"])
    season: str | None
    year: int | None

    synonyms: list[str] = Field(examples=["Konosuba"])
    external: list[AnimeExternalResponse]
    videos: list[AnimeVideoResponse]
    ost: list[AnimeOSTResponse]
    stats: AnimeStatsResponse
    schedule: list[dict]
    translated_ua: bool

    @field_validator("external")
    def external_ordering(cls, value):
        def watch_sort(item):
            order = {"Watari Anime": 0, "Anitube": 1}
            return order.get(item.text, 2)

        def reorder_watch(input_list):
            return sorted(input_list, key=watch_sort)

        general = []
        watch = []

        for entry in value:
            if entry.type == constants.EXTERNAL_GENERAL:
                general.append(entry)

            if entry.type == constants.EXTERNAL_WATCH:
                watch.append(entry)

        return general + reorder_watch(watch)
