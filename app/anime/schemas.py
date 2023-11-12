from pydantic import constr, PositiveInt
from pydantic import Field, validator
from datetime import datetime
from app import constants
from enum import Enum

from app.schemas import (
    PaginationResponse,
    CharacterResponse,
    CompanyTypeEnum,
    CompanyResponse,
    PersonResponse,
    AnimeResponse,
    ORJSONModel,
)


# Enums
class AnimeStatusEnum(str, Enum):
    announced = constants.RELEASE_STATUS_ANNOUNCED
    finished = constants.RELEASE_STATUS_FINISHED
    ongoing = constants.RELEASE_STATUS_ONGOING


class SeasonEnum(str, Enum):
    winter = constants.SEASON_WINTER
    spring = constants.SEASON_SPRING
    summer = constants.SEASON_SUMMER
    fall = constants.SEASON_FALL


class AnimeMediaEnum(str, Enum):
    special = constants.MEDIA_TYPE_SPECIAL
    movie = constants.MEDIA_TYPE_MOVIE
    music = constants.MEDIA_TYPE_MUSIC
    ova = constants.MEDIA_TYPE_OVA
    ona = constants.MEDIA_TYPE_ONA
    tv = constants.MEDIA_TYPE_TV


class AnimeAgeRatingEnum(str, Enum):
    r_plus = constants.AGE_RATING_R_PLUS
    pg_13 = constants.AGE_RATING_PG_13
    pg = constants.AGE_RATING_PG
    rx = constants.AGE_RATING_RX
    g = constants.AGE_RATING_G
    r = constants.AGE_RATING_R


class SourceEnum(str, Enum):
    digital_manga = constants.SOURCE_DIGITAL_MANGA
    picture_book = constants.SOURCE_PICTURE_BOOK
    visual_novel = constants.SOURCE_VISUAL_NOVEL
    koma4_manga = constants.SOURCE_4_KOMA_MANGA
    light_novel = constants.SOURCE_LIGHT_NOVEL
    card_game = constants.SOURCE_CARD_GAME
    web_manga = constants.SOURCE_WEB_MANGA
    original = constants.SOURCE_ORIGINAL
    manga = constants.SOURCE_MANGA
    music = constants.SOURCE_MUSIC
    novel = constants.SOURCE_NOVEL
    other = constants.SOURCE_OTHER
    radio = constants.SOURCE_RADIO
    game = constants.SOURCE_GAME
    book = constants.SOURCE_BOOK


# Args
class AnimeSearchArgs(ORJSONModel):
    query: constr(min_length=3, max_length=255) | None = None
    sort: list[str] = ["score:desc", "scored_by:desc"]
    page: int = Field(default=1, gt=0, example=1)

    years: list[PositiveInt | None] = Field(
        default=[None, None], min_items=2, max_items=2, example=[2000, 2020]
    )

    score: list[int | None] = Field(
        default=[None, None], min_items=2, max_items=2, example=[0, 10]
    )

    media_type: list[AnimeMediaEnum] = []
    rating: list[AnimeAgeRatingEnum] = []
    status: list[AnimeStatusEnum] = []
    source: list[SourceEnum] = []
    season: list[SeasonEnum] = []

    producers: list[str] = []
    studios: list[str] = []
    genres: list[str] = []

    @validator("years")
    def validate_years(cls, years):
        if all(year is not None for year in years) and years[0] > years[1]:
            raise ValueError(
                "The first year must be less than the second year."
            )

        return years

    @validator("score")
    def validate_score(cls, scores):
        if all(score is not None for score in scores) and scores[0] > scores[1]:
            raise ValueError(
                "The first score must be less than the second score."
            )

        if scores[0] and scores[0] < 0:
            raise ValueError("Score can't be less than 0.")

        if scores[1] and scores[1] > 10:
            raise ValueError("Score can't be more than 10.")

        return scores

    @validator("sort")
    def validate_sort(cls, sort_list):
        valid_fields = ["score", "scored_by"]
        valid_orders = ["asc", "desc"]

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
class AnimeEpisodeResponse(ORJSONModel):
    aired: datetime | None = Field(example=1686088809)
    title_ua: str | None = Field(
        example="Самопроголошена богиня і переродження в паралельному світі!"
    )
    title_en: str | None = Field(
        example="This Self-Proclaimed Goddess and Reincarnation in Another World!"  # noqa: E501
    )
    title_ja: str | None = Field(
        example="Kono Jishou Megami to Isekai Tenshou wo!"
    )
    index: int = Field(example=1)


class AnimeEpisodesListResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[AnimeEpisodeResponse]


class AnimeCharacterResponse(ORJSONModel):
    main: bool = Field(example=True)
    character: CharacterResponse


class RoleResponse(ORJSONModel):
    name_ua: str | None
    name_en: str | None
    slug: str


class AnimeStaffResponse(ORJSONModel):
    person: PersonResponse | None
    roles: list[RoleResponse]


class GenreResponse(ORJSONModel):
    name_en: str | None = Field(example="Comedy")
    name_ua: str | None = Field(example="Комедія")
    slug: str = Field(example="comedy")
    type: str = Field(example="genre")


class GenreListResposne(ORJSONModel):
    list: list[GenreResponse]


class AnimeCompanyResponse(ORJSONModel):
    company: CompanyResponse
    type: CompanyTypeEnum


class AnimeCharacterPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[AnimeCharacterResponse]


class AnimeStaffPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[AnimeStaffResponse]


class AnimeSearchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[AnimeResponse]


class AnimeStatsResponse(ORJSONModel):
    completed: int = Field(example=1502335)
    watching: int = Field(example=83106)
    planned: int = Field(example=206073)
    dropped: int = Field(example=33676)
    on_hold: int = Field(example=30222)
    score_1: int = Field(example=3087)
    score_2: int = Field(example=2633)
    score_3: int = Field(example=4583)
    score_4: int = Field(example=11343)
    score_5: int = Field(example=26509)
    score_6: int = Field(example=68501)
    score_7: int = Field(example=211113)
    score_8: int = Field(example=398095)
    score_9: int = Field(example=298198)
    score_10: int = Field(example=184038)


class AnimeExternalResponse(ORJSONModel):
    url: str = Field(example="https://www.konosuba.com/")
    text: str = Field(example="Official Site")


class AnimeVideoResponse(ORJSONModel):
    url: str = Field(example="https://youtu.be/_4W1OQoDEDg")
    title: str | None = Field(example="ED 2 (Artist ver.)")
    description: str | None = Field(example="...")
    video_type: str = Field(example="video_music")


class AnimeOSTResponse(ORJSONModel):
    index: int = Field(example=1)
    title: str | None = Field(example="fantastic dreamer")
    author: str | None = Field(example="Machico")
    spotify: str | None = Field(
        example="https://open.spotify.com/track/3BIhcWQV2hGRoEXdLL3Fzw"
    )
    ost_type: str = Field(example="opening")


class AnimeInfoResponse(ORJSONModel):
    companies: list[AnimeCompanyResponse]
    genres: list[GenreResponse]

    start_date: datetime | None = Field(example=1686088809)
    end_date: datetime | None = Field(example=1686088809)

    episodes_released: int | None = Field(example=10)
    episodes_total: int | None = Field(example=10)
    synopsis_en: str | None = Field(example="...")
    synopsis_ua: str | None = Field(example="...")
    media_type: str | None = Field(example="tv")
    title_ua: str | None = Field(
        example="Цей прекрасний світ, благословенний Богом!"
    )
    title_en: str | None = Field(
        example="KonoSuba: God's Blessing on This Wonderful World!"
    )
    title_ja: str | None = Field(
        example="Kono Subarashii Sekai ni Shukufuku wo!"
    )
    duration: int | None = Field(example=23)
    poster: str | None = Field(example="https://cdn.hikka.io/hikka.jpg")
    status: str | None = Field(example="finished")
    source: str | None = Field(example="light_novel")
    rating: str | None = Field(example="pg_13")
    has_franchise: bool = Field(example=True)
    scored_by: int = Field(example=1210150)
    score: float = Field(example=8.11)
    nsfw: bool = Field(example=False)
    slug: str = Field(example="kono-subarashii-sekai-ni-shukufuku-wo-123456")

    synonyms: list[str] = Field(example=["Konosuba"])
    external: list[AnimeExternalResponse]
    videos: list[AnimeVideoResponse]
    ost: list[AnimeOSTResponse]
    stats: AnimeStatsResponse
