from app.common.schemas.company import CompanyResponse
from app.common.schemas.watch import WatchResponseBase
from app.common.schemas.genre import GenreResponse
from app.schemas import CustomModel, datetime_pd
from app.schemas import PaginationResponse
from app.schemas import YearsSeasonsMixin
from pydantic import field_validator
from pydantic import Field
from typing import Literal
from app import constants
from enum import Enum

from app.schemas import (
    ContentStatusEnum,
    SeasonEnum,
)


# Enums
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


class AnimeAgeRatingEnum(str, Enum):
    r_plus = constants.AGE_RATING_R_PLUS
    pg_13 = constants.AGE_RATING_PG_13
    pg = constants.AGE_RATING_PG
    rx = constants.AGE_RATING_RX
    g = constants.AGE_RATING_G
    r = constants.AGE_RATING_R


class AnimeVideoTypeEnum(str, Enum):
    video_promo = constants.VIDEO_PROMO
    video_music = constants.VIDEO_MUSIC


class AnimeMediaEnum(str, Enum):
    special = constants.MEDIA_TYPE_SPECIAL
    movie = constants.MEDIA_TYPE_MOVIE
    music = constants.MEDIA_TYPE_MUSIC
    ova = constants.MEDIA_TYPE_OVA
    ona = constants.MEDIA_TYPE_ONA
    tv = constants.MEDIA_TYPE_TV


# Args
class AnimeSearchArgsBase(CustomModel, YearsSeasonsMixin):
    include_multiseason: bool = False
    only_translated: bool = False

    score: list[int | None] = Field(
        default=[None, None],
        min_length=2,
        max_length=2,
        examples=[[0, 10]],
    )

    native_score: list[int | None] = Field(
        default=[None, None],
        min_length=2,
        max_length=2,
        examples=[[0, 10]],
    )

    media_type: list[AnimeMediaEnum] = []
    rating: list[AnimeAgeRatingEnum] = []
    status: list[ContentStatusEnum] = []
    source: list[SourceEnum] = []
    season: list[SeasonEnum] = []

    producers: list[str] = []
    studios: list[str] = []
    genres: list[str] = []

    @field_validator("score", "native_score")
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


# Responses
class AnimeVideoResponse(CustomModel):
    url: str = Field(examples=["https://youtu.be/_4W1OQoDEDg"])
    title: str | None = Field(examples=["ED 2 (Artist ver.)"])
    description: str | None = Field(examples=["..."])
    video_type: AnimeVideoTypeEnum


class AnimeResponse(CustomModel):
    data_type: Literal["anime"]
    media_type: str | None = Field(examples=["tv"])
    title_native: str | None = Field(examples=["この素晴らしい世界に祝福を！"])
    title_ua: str | None = Field(
        examples=["Цей прекрасний світ, благословенний Богом!"]
    )
    title_en: str | None = Field(
        examples=["KonoSuba: God's Blessing on This Wonderful World!"]
    )
    title_ja: str | None = Field(
        examples=["Kono Subarashii Sekai ni Shukufuku wo!"]
    )
    episodes_released: int | None = Field(examples=["10"])
    episodes_total: int | None = Field(examples=["10"])
    image: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    status: str | None = Field(examples=["finished"])
    native_scored_by: int = Field(examples=[1210150])
    native_score: float = Field(examples=[8.11])
    scored_by: int = Field(examples=[1210150])
    score: float = Field(examples=[8.11])
    slug: str = Field(examples=["kono-subarashii-sekai-ni-shukufuku-wo-123456"])
    start_date: datetime_pd | None
    end_date: datetime_pd | None
    created: datetime_pd | None
    updated: datetime_pd | None
    translated_ua: bool
    season: str | None
    source: str | None
    rating: str | None
    year: int | None
    mal_id: int

    studios: list[CompanyResponse]
    genres: list[GenreResponse]
    synopsis_en: str | None
    synopsis_ua: str | None


class AnimeResponseWithWatch(AnimeResponse):
    watch: list[WatchResponseBase]


class AnimePaginationResponse(CustomModel):
    list: list[AnimeResponseWithWatch]
    pagination: PaginationResponse
