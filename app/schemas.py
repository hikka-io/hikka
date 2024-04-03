from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta
from pydantic import model_serializer
from pydantic import Field, EmailStr
from pydantic import field_validator
from pydantic import PositiveInt
from typing import Callable
from . import constants
from enum import Enum
from . import utils


# Custom Pydantic model
class CustomModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        from_attributes=True,
        extra="forbid",
    )

    def serializable_dict(self, **kwargs):
        default_dict = self.model_dump()
        return jsonable_encoder(default_dict)

    @model_serializer(mode="wrap")
    def serialize(self, original_serializer: Callable) -> dict:
        # Based on https://github.com/pydantic/pydantic/discussions/7199#discussioncomment-6841388

        result = original_serializer(self)

        for field_name, field_info in self.model_fields.items():
            if type(getattr(self, field_name)) == datetime:
                result[field_name] = utils.to_timestamp(
                    getattr(self, field_name)
                )

            if type(getattr(self, field_name)) == timedelta:
                result[field_name] = int(
                    getattr(self, field_name).total_seconds()
                )

        return result


class CustomModelExtraIgnore(CustomModel):
    model_config = ConfigDict(extra="ignore")


# Enums
class CompanyTypeEnum(str, Enum):
    producer = constants.COMPANY_ANIME_PRODUCER
    studio = constants.COMPANY_ANIME_STUDIO


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


class CollectionVisibilityEnum(str, Enum):
    visibility_unlisted = constants.COLLECTION_UNLISTED
    visibility_private = constants.COLLECTION_PRIVATE
    visibility_public = constants.COLLECTION_PUBLIC


# Args
class PaginationArgs(CustomModel):
    page: int = Field(default=1, gt=0, examples=[1])


class QuerySearchArgs(CustomModel):
    query: str | None = Field(default=None, min_length=3, max_length=255)


class UsernameArgs(CustomModel):
    username: str = Field(
        pattern="^[A-Za-z][A-Za-z0-9_]{4,63}$", examples=["hikka"]
    )


class EmailArgs(CustomModel):
    email: EmailStr = Field(examples=["hikka@email.com"])

    @field_validator("email")
    @classmethod
    def check_email(cls, value: EmailStr) -> EmailStr:
        if "+" in value:
            raise ValueError("Email contains uacceptable characters")

        return value


class TokenArgs(CustomModel):
    token: str = Field(examples=["CQE-CTXVFCYoUpxz_6VKrHhzHaUZv68XvxV-3AvQbnA"])


class PasswordArgs(CustomModel):
    password: str = Field(min_length=8, max_length=256, examples=["password"])


class AnimeSearchArgsBase(CustomModel):
    include_multiseason: bool = False
    only_translated: bool = False

    years: list[PositiveInt | None] | None = Field(
        default=[None, None],
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
        if not years:
            return [None, None]

        if len(years) == 0:
            return [None, None]

        if len(years) != 2:
            raise ValueError("Lenght of years list must be 2.")

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


# Responses
class PaginationResponse(CustomModel):
    total: int = Field(examples=[20])
    pages: int = Field(examples=[2])
    page: int = Field(examples=[1])


class WatchResponseBase(CustomModel):
    reference: str = Field(examples=["c773d0bf-1c42-4c18-aec8-1bdd8cb0a434"])
    note: str | None = Field(max_length=2048, examples=["🤯"])
    updated: datetime = Field(examples=[1686088809])
    created: datetime = Field(examples=[1686088809])
    status: str = Field(examples=["watching"])
    rewatches: int = Field(examples=[2])
    duration: int = Field(examples=[24])
    episodes: int = Field(examples=[3])
    score: int = Field(examples=[8])


class AnimeResponse(CustomModel):
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
    episodes_released: int | None = Field(examples=["10"])
    episodes_total: int | None = Field(examples=["10"])
    poster: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    status: str | None = Field(examples=["finished"])
    scored_by: int = Field(examples=[1210150])
    score: float = Field(examples=[8.11])
    slug: str = Field(examples=["kono-subarashii-sekai-ni-shukufuku-wo-123456"])
    translated_ua: bool
    season: str | None
    source: str | None
    rating: str | None
    year: int | None


class AnimeResponseWithWatch(AnimeResponse):
    watch: list[WatchResponseBase]


class AnimePaginationResponse(CustomModel):
    list: list[AnimeResponseWithWatch]
    pagination: PaginationResponse


class CharacterResponse(CustomModel):
    name_ua: str | None = Field(examples=["Меґумін"])
    name_en: str | None = Field(examples=["Megumin"])
    name_ja: str | None = Field(examples=["めぐみん"])
    image: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    slug: str = Field(examples=["megumin-123456"])
    synonyms: list[str]


class PersonResponse(CustomModel):
    name_native: str | None = Field(examples=["高橋 李依"])
    name_ua: str | None = Field(examples=["Ріє Такахаші"])
    name_en: str | None = Field(examples=["Rie Takahashi"])
    image: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    slug: str = Field(examples=["rie-takahashi-123456"])
    synonyms: list[str]


class RoleResponse(CustomModel):
    name_ua: str | None
    name_en: str | None
    weight: int | None
    slug: str


class AnimeStaffResponse(CustomModel):
    person: PersonResponse | None
    roles: list[RoleResponse]
    weight: int | None


class SuccessResponse(CustomModel):
    success: bool = Field(examples=[True])


class CompanyResponse(CustomModel):
    image: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    slug: str = Field(examples=["hikka-inc-123456"])
    name: str = Field(examples=["Hikka Inc."])


class UserResponse(CustomModel):
    reference: str = Field(examples=["c773d0bf-1c42-4c18-aec8-1bdd8cb0a434"])
    updated: datetime | None = Field(examples=[1686088809])
    description: str | None = Field(examples=["Hikka"])
    username: str | None = Field(examples=["hikka"])
    created: datetime = Field(examples=[1686088809])
    cover: str | None
    active: bool
    avatar: str
    role: str


class AnimeExternalResponse(CustomModel):
    url: str = Field(examples=["https://www.konosuba.com/"])
    text: str = Field(examples=["Official Site"])
    type: str


class AnimeVideoResponse(CustomModel):
    url: str = Field(examples=["https://youtu.be/_4W1OQoDEDg"])
    title: str | None = Field(examples=["ED 2 (Artist ver.)"])
    description: str | None = Field(examples=["..."])
    video_type: str = Field(examples=["video_music"])


class CommentResponse(CustomModel):
    replies: list["CommentResponse"] = []
    total_replies: int = 0
    author: UserResponse
    updated: datetime
    created: datetime
    text: str | None
    reference: str
    my_score: int
    hidden: bool
    score: int
    depth: int


# Collections
class CollectionContentResponse(CustomModel):
    content: AnimeResponseWithWatch | CharacterResponse | PersonResponse
    comment: str | None
    label: str | None
    content_type: str
    order: int


class CollectionResponse(CustomModel):
    visibility: CollectionVisibilityEnum
    labels_order: list[str]
    author: UserResponse
    comments_count: int
    created: datetime
    updated: datetime
    content_type: str
    description: str
    vote_score: int
    tags: list[str]
    reference: str
    my_score: int
    spoiler: bool
    entries: int
    title: str
    nsfw: bool

    collection: list[CollectionContentResponse]

    @field_validator("collection")
    def collection_ordering(cls, collection):
        return sorted(collection, key=lambda c: c.order)
