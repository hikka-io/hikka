from pydantic import Field, field_validator
from pydantic import constr, PositiveInt
from datetime import datetime
from app import constants
from enum import Enum

from app.schemas import (
    AnimeResponseWithWatch,
    PaginationResponse,
    CharacterResponse,
    CompanyTypeEnum,
    CompanyResponse,
    PersonResponse,
    CustomModel,
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
class AnimeSearchArgs(CustomModel):
    query: constr(min_length=3, max_length=255) | None = None
    sort: list[str] = ["score:desc", "scored_by:desc"]

    years: list[PositiveInt | None] = Field(
        default=[None, None],
        min_length=2,
        max_length=2,
        examples=[[2000, 2020]],
    )

    score: list[int | None] = Field(
        default=[None, None],
        min_length=2,
        max_length=2,
        examples=[[0, 10]],
    )

    media_type: list[AnimeMediaEnum] = []
    rating: list[AnimeAgeRatingEnum] = []
    status: list[AnimeStatusEnum] = []
    source: list[SourceEnum] = []
    season: list[SeasonEnum] = []

    producers: list[str] = []
    studios: list[str] = []
    genres: list[str] = []

    @field_validator("years")
    def validate_years(cls, years):
        if all(year is not None for year in years) and years[0] > years[1]:
            raise ValueError(
                "The first year must be less than the second year."
            )

        return years

    @field_validator("score")
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

    @field_validator("sort")
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
class AnimeEpisodeResponse(CustomModel):
    aired: datetime | None = Field(examples=[1686088809])
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


class RoleResponse(CustomModel):
    name_ua: str | None
    name_en: str | None
    weight: int | None
    slug: str


class AnimeStaffResponse(CustomModel):
    person: PersonResponse | None
    roles: list[RoleResponse]
    weight: int | None


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


class AnimeSearchPaginationResponse(CustomModel):
    list: list[AnimeResponseWithWatch]
    pagination: PaginationResponse


class AnimeStatsResponse(CustomModel):
    completed: int = Field(examples=[1502335])
    watching: int = Field(examples=[83106])
    planned: int = Field(examples=[206073])
    dropped: int = Field(examples=[33676])
    on_hold: int = Field(examples=[30222])
    score_1: int = Field(examples=[3087])
    score_2: int = Field(examples=[2633])
    score_3: int = Field(examples=[4583])
    score_4: int = Field(examples=[11343])
    score_5: int = Field(examples=[26509])
    score_6: int = Field(examples=[68501])
    score_7: int = Field(examples=[211113])
    score_8: int = Field(examples=[398095])
    score_9: int = Field(examples=[298198])
    score_10: int = Field(examples=[184038])


class AnimeExternalResponse(CustomModel):
    url: str = Field(examples=["https://www.konosuba.com/"])
    text: str = Field(examples=["Official Site"])


class AnimeVideoResponse(CustomModel):
    url: str = Field(examples=["https://youtu.be/_4W1OQoDEDg"])
    title: str | None = Field(examples=["ED 2 (Artist ver.)"])
    description: str | None = Field(examples=["..."])
    video_type: str = Field(examples=["video_music"])


class AnimeOSTResponse(CustomModel):
    index: int = Field(examples=[1])
    title: str | None = Field(examples=["fantastic dreamer"])
    author: str | None = Field(examples=["Machico"])
    spotify: str | None = Field(
        examples=["https://open.spotify.com/track/3BIhcWQV2hGRoEXdLL3Fzw"]
    )
    ost_type: str = Field(examples=["opening"])


class AnimeInfoResponse(CustomModel):
    companies: list[AnimeCompanyResponse]
    genres: list[GenreResponse]

    start_date: datetime | None = Field(examples=[1686088809])
    end_date: datetime | None = Field(examples=[1686088809])

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

    synonyms: list[str] = Field(examples=["Konosuba"])
    external: list[AnimeExternalResponse]
    videos: list[AnimeVideoResponse]
    ost: list[AnimeOSTResponse]
    stats: AnimeStatsResponse
