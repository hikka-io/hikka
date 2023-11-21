from fastapi.encoders import jsonable_encoder
from pydantic import Field, EmailStr, constr
from pydantic import BaseModel, ConfigDict
from pydantic import model_serializer
from datetime import datetime
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

        return result


# Enums
class CompanyTypeEnum(str, Enum):
    producer = constants.COMPANY_ANIME_PRODUCER
    studio = constants.COMPANY_ANIME_STUDIO


# Args
class PaginationArgs(CustomModel):
    page: int = Field(default=1, gt=0, examples=[1])


class QuerySearchArgs(CustomModel):
    query: constr(min_length=3, max_length=255) | None = None
    page: int = Field(default=1, gt=0, examples=[1])


class UsernameArgs(CustomModel):
    username: str = Field(
        pattern="^[A-Za-z][A-Za-z0-9_]{4,63}$", examples=["hikka"]
    )


class EmailArgs(CustomModel):
    email: EmailStr = Field(examples=["hikka@email.com"])


# Responses
class PaginationResponse(CustomModel):
    total: int = Field(examples=[20])
    pages: int = Field(examples=[2])
    page: int = Field(examples=[1])


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
    season: str | None
    source: str | None
    rating: str | None
    year: int | None


class CharacterResponse(CustomModel):
    name_ua: str | None = Field(examples=["Меґумін"])
    name_en: str | None = Field(examples=["Megumin"])
    name_ja: str | None = Field(examples=["めぐみん"])
    image: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    slug: str = Field(examples=["megumin-123456"])


class PersonResponse(CustomModel):
    name_native: str | None = Field(examples=["高橋 李依"])
    name_ua: str | None = Field(examples=["Ріє Такахаші"])
    name_en: str | None = Field(examples=["Rie Takahashi"])
    image: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    slug: str = Field(examples=["rie-takahashi-123456"])


class AnimeFavouriteResponse(CustomModel):
    reference: str = Field(examples=["c773d0bf-1c42-4c18-aec8-1bdd8cb0a434"])
    created: datetime = Field(examples=[1686088809])
    anime: AnimeResponse


class SuccessResponse(CustomModel):
    success: bool = Field(examples=[True])


class CompanyResponse(CustomModel):
    image: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    slug: str = Field(examples=["hikka-inc-123456"])
    name: str = Field(examples=["Hikka Inc."])


class UserResponse(CustomModel):
    reference: str = Field(examples=["c773d0bf-1c42-4c18-aec8-1bdd8cb0a434"])
    description: str | None = Field(examples=["Hikka"])
    username: str | None = Field(examples=["hikka"])
    created: datetime = Field(examples=[1686088809])
    avatar: str
    role: str
