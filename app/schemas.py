from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta
from pydantic import PlainSerializer
from pydantic import Field, EmailStr
from pydantic import field_validator
from pydantic import BeforeValidator
from pydantic import PositiveInt
from typing import Annotated
from . import constants
from enum import Enum
from . import utils


# Custom field types
UnixTimestamp = Annotated[datetime, BeforeValidator(utils.from_timestamp)]


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


class ExternalTypeEnum(str, Enum):
    general = constants.EXTERNAL_GENERAL
    watch = constants.EXTERNAL_WATCH
    read = constants.EXTERNAL_READ


# Mixins
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


# Responses
class PaginationResponse(CustomModel):
    total: int = Field(examples=[20])
    pages: int = Field(examples=[2])
    page: int = Field(examples=[1])


class SuccessResponse(CustomModel):
    success: bool = Field(examples=[True])


class ExternalResponse(CustomModel):
    url: str = Field(examples=["https://www.konosuba.com/"])
    text: str = Field(examples=["Official Site"])
    type: ExternalTypeEnum
