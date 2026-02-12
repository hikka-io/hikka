from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta
from pydantic import PlainSerializer
from pydantic import Field, EmailStr
from pydantic import field_validator
from pydantic import PositiveInt
from typing import Annotated
from . import constants
from enum import Enum
from . import utils


# Custom Pydantic serializers
datetime_pd = Annotated[
    datetime,
    PlainSerializer(
        lambda x: utils.to_timestamp(x),
        return_type=int,
    ),
]

timedelta_pd = Annotated[
    timedelta,
    PlainSerializer(
        lambda x: int(x.total_seconds()),
        return_type=int,
    ),
]


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


class ContentStatusEnum(str, Enum):
    discontinued = constants.RELEASE_STATUS_DISCONTINUED
    announced = constants.RELEASE_STATUS_ANNOUNCED
    finished = constants.RELEASE_STATUS_FINISHED
    ongoing = constants.RELEASE_STATUS_ONGOING
    paused = constants.RELEASE_STATUS_PAUSED


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


class MangaMediaEnum(str, Enum):
    one_shot = constants.MEDIA_TYPE_ONE_SHOT
    doujin = constants.MEDIA_TYPE_DOUJIN
    manhua = constants.MEDIA_TYPE_MANHUA
    manhwa = constants.MEDIA_TYPE_MANHWA
    manga = constants.MEDIA_TYPE_MANGA


class NovelMediaEnum(str, Enum):
    light_novel = constants.MEDIA_TYPE_LIGHT_NOVEL
    novel = constants.MEDIA_TYPE_NOVEL


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


# Mixins
class DataTypeMixin:
    data_type: str


class YearsMixin:
    years: list[PositiveInt | None] | None = Field(
        default=[None, None],
        examples=[[2000, 2020]],
    )

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


class YearsSeasonsMixin:
    years: list[tuple[SeasonEnum, PositiveInt]] | list[PositiveInt | None] = (
        Field(
            default=[None, None],
            examples=[
                [2014, 2024],
                [["summer", 2014], ["winter", 2024]],
            ],
        )
    )

    @field_validator("years")
    def validate_years(cls, years):
        if not years or len(years) == 0:
            return [None, None]

        if len(years) != 2:
            raise ValueError("Length of years list must be 2.")

        def extract_year(elem):
            """Return the numeric year from either a SimpleYear or ComplexFilter."""

            if isinstance(elem, tuple):
                if len(elem) != 2:
                    raise ValueError("Complex filter must be ['season', year].")

                return elem[1]

            return elem

        first, second = years
        y1 = extract_year(first)
        y2 = extract_year(second)

        if isinstance(y1, int) and isinstance(y2, int) and y1 > y2:
            raise ValueError("The first year must be ≤ the second year.")

        return years


class MangaSearchBaseMixin:
    media_type: list[MangaMediaEnum] = []
    status: list[ContentStatusEnum] = []
    only_translated: bool = False
    magazines: list[str] = []
    genres: list[str] = []

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


class NovelSearchBaseMixin:
    media_type: list[NovelMediaEnum] = []
    status: list[ContentStatusEnum] = []
    only_translated: bool = False
    magazines: list[str] = []
    genres: list[str] = []

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


# Args
class PaginationArgs(CustomModel):
    page: int = Field(default=1, gt=0, examples=[1])


class QuerySearchArgs(CustomModel):
    query: str | None = Field(default=None, min_length=2, max_length=255)


class QuerySearchRequiredArgs(CustomModel):
    query: str = Field(min_length=3, max_length=255)


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
    status: list[AnimeStatusEnum] = []
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


class MangaSearchArgs(
    QuerySearchArgs,
    MangaSearchBaseMixin,
    YearsMixin,
):
    sort: list[str] = ["score:desc", "scored_by:desc"]

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        return utils.check_sort(
            sort_list,
            [
                "native_scored_by",
                "native_score",
                "media_type",
                "start_date",
                "scored_by",
                "created",
                "updated",
                "score",
            ],
        )

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


class NovelSearchArgs(
    QuerySearchArgs,
    NovelSearchBaseMixin,
    YearsMixin,
):
    sort: list[str] = ["score:desc", "scored_by:desc"]

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        return utils.check_sort(
            sort_list,
            [
                "native_scored_by",
                "native_score",
                "media_type",
                "start_date",
                "scored_by",
                "created",
                "updated",
                "score",
            ],
        )

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
class PaginationResponse(CustomModel):
    total: int = Field(examples=[20])
    pages: int = Field(examples=[2])
    page: int = Field(examples=[1])


class WatchResponseBase(CustomModel):
    reference: str = Field(examples=["c773d0bf-1c42-4c18-aec8-1bdd8cb0a434"])
    note: str | None = Field(max_length=2048, examples=["🤯"])
    updated: datetime_pd = Field(examples=[1686088809])
    created: datetime_pd = Field(examples=[1686088809])
    status: str = Field(examples=["watching"])
    rewatches: int = Field(examples=[2])
    duration: int = Field(examples=[24])
    episodes: int = Field(examples=[3])
    score: int = Field(examples=[8])
    start_date: datetime_pd | None
    end_date: datetime_pd | None


class ReadResponseBase(CustomModel):
    reference: str = Field(examples=["c773d0bf-1c42-4c18-aec8-1bdd8cb0a434"])
    note: str | None = Field(max_length=2048, examples=["🤯"])
    updated: datetime_pd = Field(examples=[1686088809])
    created: datetime_pd = Field(examples=[1686088809])
    status: str = Field(examples=["reading"])
    chapters: int = Field(examples=[3])
    volumes: int = Field(examples=[3])
    rereads: int = Field(examples=[2])
    score: int = Field(examples=[8])


class AnimeResponse(CustomModel, DataTypeMixin):
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


class MangaResponse(CustomModel, DataTypeMixin):
    start_date: datetime_pd | None
    end_date: datetime_pd | None
    created: datetime_pd | None
    updated: datetime_pd | None
    title_original: str | None
    media_type: str | None
    native_scored_by: int
    title_ua: str | None
    title_en: str | None
    chapters: int | None
    volumes: int | None
    translated_ua: bool
    native_score: float
    status: str | None
    image: str | None
    year: int | None
    scored_by: int
    score: float
    mal_id: int
    slug: str


class NovelResponse(CustomModel, DataTypeMixin):
    start_date: datetime_pd | None
    end_date: datetime_pd | None
    created: datetime_pd | None
    updated: datetime_pd | None
    title_original: str | None
    media_type: str | None
    native_scored_by: int
    title_ua: str | None
    title_en: str | None
    chapters: int | None
    volumes: int | None
    translated_ua: bool
    native_score: float
    status: str | None
    image: str | None
    year: int | None
    scored_by: int
    score: float
    mal_id: int
    slug: str


class AnimeResponseWithWatch(AnimeResponse):
    watch: list[WatchResponseBase]


class MangaResponseWithRead(MangaResponse):
    read: list[ReadResponseBase]


class NovelResponseWithRead(NovelResponse):
    read: list[ReadResponseBase]


class AnimePaginationResponse(CustomModel):
    list: list[AnimeResponseWithWatch]
    pagination: PaginationResponse


class CharacterResponse(CustomModel, DataTypeMixin):
    name_ua: str | None = Field(examples=["Меґумін"])
    name_en: str | None = Field(examples=["Megumin"])
    name_ja: str | None = Field(examples=["めぐみん"])
    image: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    slug: str = Field(examples=["megumin-123456"])
    synonyms: list[str]


class PersonResponse(CustomModel, DataTypeMixin):
    name_native: str | None = Field(examples=["高橋 李依"])
    name_ua: str | None = Field(examples=["Ріє Такахаші"])
    name_en: str | None = Field(examples=["Rie Takahashi"])
    image: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    slug: str = Field(examples=["rie-takahashi-123456"])
    description_ua: str | None
    synonyms: list[str]


class RoleResponse(CustomModel):
    name_ua: str | None
    name_en: str | None
    weight: int | None
    slug: str


class ContentAuthorResponse(CustomModel):
    roles: list[RoleResponse]
    person: PersonResponse


class AnimeStaffResponse(ContentAuthorResponse):
    weight: int | None


class SuccessResponse(CustomModel):
    success: bool = Field(examples=[True])


class CompanyResponse(CustomModel):
    image: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    slug: str = Field(examples=["hikka-inc-123456"])
    name: str = Field(examples=["Hikka Inc."])


class UserResponse(CustomModel):
    reference: str = Field(examples=["c773d0bf-1c42-4c18-aec8-1bdd8cb0a434"])
    updated: datetime_pd | None = Field(examples=[1686088809])
    created: datetime_pd = Field(examples=[1686088809])
    description: str | None = Field(examples=["Hikka"])
    username: str | None = Field(examples=["hikka"])
    cover: str | None
    active: bool
    avatar: str
    role: str


class FollowUserResponse(UserResponse):
    is_followed: bool


class ExternalResponse(CustomModel):
    url: str = Field(examples=["https://www.konosuba.com/"])
    text: str = Field(examples=["Official Site"])
    type: str


class AnimeVideoResponse(CustomModel):
    url: str = Field(examples=["https://youtu.be/_4W1OQoDEDg"])
    title: str | None = Field(examples=["ED 2 (Artist ver.)"])
    description: str | None = Field(examples=["..."])
    video_type: str = Field(examples=["video_music"])


# Collections
class CollectionContentResponse(CustomModel):
    comment: str | None
    label: str | None
    content_type: str
    order: int

    content: (
        AnimeResponseWithWatch
        | MangaResponseWithRead
        | NovelResponseWithRead
        | CharacterResponse
        | PersonResponse
    )


class CollectionResponse(CustomModel, DataTypeMixin):
    visibility: CollectionVisibilityEnum
    author: FollowUserResponse
    labels_order: list[str]
    created: datetime_pd
    updated: datetime_pd
    comments_count: int
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


class GenreResponse(CustomModel):
    name_ua: str | None = Field(examples=["Комедія"])
    name_en: str | None = Field(examples=["Comedy"])
    slug: str = Field(examples=["comedy"])
    type: str = Field(examples=["genre"])


class GenreListResponse(CustomModel):
    list: list[GenreResponse]


class ReadStatsResponse(CustomModel):
    completed: int = Field(examples=[1502335], default=0)
    reading: int = Field(examples=[83106], default=0)
    on_hold: int = Field(examples=[206073], default=0)
    dropped: int = Field(examples=[33676], default=0)
    planned: int = Field(examples=[30222], default=0)
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


class MagazineResponse(CustomModel):
    name_en: str
    slug: str


class ContentCharacterResponse(CustomModel):
    main: bool = Field(examples=[True])
    character: CharacterResponse


class ContentCharacterPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[ContentCharacterResponse]


class ClientResponse(CustomModel):
    reference: str
    name: str
    description: str
    verified: bool

    user: UserResponse

    created: datetime_pd
    updated: datetime_pd
