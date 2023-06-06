from pydantic import constr, PositiveInt
from pydantic import Field, validator
from app.schemas import ORJSONModel
from datetime import datetime
from app import constants
from typing import Union
from enum import Enum

from app.schemas import (
    PaginationResponse,
    CharacterResponse,
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
    query: Union[constr(min_length=3, max_length=255), None] = None
    sort: list[str] = ["score:desc", "scored_by:desc"]
    page: int = Field(default=1, gt=0)

    years: list[Union[PositiveInt, None]] = Field(
        default=[None, None], min_items=2, max_items=2
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

    @validator("sort")
    def validate_sort(cls, sort_list):
        valid_fields = ["score", "scored_by"]
        valid_orders = ["asc", "desc"]

        if len(sort_list) != len(set(sort_list)):
            raise ValueError(f"Invalid sort: duplicates")

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
    aired: Union[datetime, None]
    title_ua: Union[str, None]
    title_en: Union[str, None]
    title_ja: Union[str, None]
    index: int


class AnimeEpisodesListResponse(ORJSONModel):
    list: list[AnimeEpisodeResponse]


class AnimeCharacterResponse(ORJSONModel):
    character: CharacterResponse
    main: bool


class AnimeStaffResponse(ORJSONModel):
    person: PersonResponse
    role: str


class GenreResponse(ORJSONModel):
    name_en: Union[str, None]
    name_ua: Union[str, None]
    slug: str


class AnimeCompanyResponse(ORJSONModel):
    company: CompanyResponse
    type: str


class AnimeCharacterPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[AnimeCharacterResponse]


class AnimeStaffPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[AnimeStaffResponse]


class AnimeSearchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[AnimeResponse]


class AnimeInfoResponse(ORJSONModel):
    companies: list[AnimeCompanyResponse]
    genres: list[GenreResponse]

    start_date: Union[datetime, None]
    end_date: Union[datetime, None]

    total_episodes: Union[int, None]
    synopsis_en: Union[str, None]
    synopsis_ua: Union[str, None]
    media_type: Union[str, None]
    franchise: Union[str, None]
    title_ua: Union[str, None]
    title_en: Union[str, None]
    title_ja: Union[str, None]
    episodes: Union[int, None]
    duration: Union[int, None]
    poster: Union[str, None]
    status: Union[str, None]
    source: Union[str, None]
    rating: Union[str, None]
    has_franchise: bool
    scored_by: int
    score: float
    nsfw: bool
    slug: str

    synonyms: list[str]
    external: list[dict]
    videos: list[dict]
    ost: list[dict]
    stats: dict
