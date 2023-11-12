from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict
from pydantic import model_serializer
from pydantic import Field, constr
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
            if field_info.annotation == datetime:
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
    page: int = Field(default=1, gt=0, example=1)


# Responses
class PaginationResponse(CustomModel):
    total: int = Field(example=20)
    pages: int = Field(example=2)
    page: int = Field(example=1)


class QuerySearchArgs(CustomModel):
    query: constr(min_length=3, max_length=255) | None = None
    page: int = Field(default=1, gt=0, example=1)


class AnimeResponse(CustomModel):
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
    episodes_released: int | None = Field(example="10")
    episodes_total: int | None = Field(example="10")
    poster: str | None = Field(example="https://cdn.hikka.io/hikka.jpg")
    status: str | None = Field(example="finished")
    scored_by: int = Field(example=1210150)
    score: float = Field(example=8.11)
    slug: str = Field(example="kono-subarashii-sekai-ni-shukufuku-wo-123456")
    season: str | None
    source: str | None
    rating: str | None
    year: int | None


class CharacterResponse(CustomModel):
    name_ua: str | None = Field(example="Меґумін")
    name_en: str | None = Field(example="Megumin")
    name_ja: str | None = Field(example="めぐみん")
    image: str | None = Field(example="https://cdn.hikka.io/hikka.jpg")
    slug: str = Field(example="megumin-123456")


class PersonResponse(CustomModel):
    name_native: str | None = Field(example="高橋 李依")
    name_ua: str | None = Field(example="Ріє Такахаші")
    name_en: str | None = Field(example="Rie Takahashi")
    image: str | None = Field(example="https://cdn.hikka.io/hikka.jpg")
    slug: str = Field(example="rie-takahashi-123456")


class AnimeFavouriteResponse(CustomModel):
    reference: str = Field(example="c773d0bf-1c42-4c18-aec8-1bdd8cb0a434")
    created: datetime = Field(example=1686088809)
    anime: AnimeResponse


class SuccessResponse(CustomModel):
    success: bool = Field(example=True)


class CompanyResponse(CustomModel):
    image: str | None = Field(example="https://cdn.hikka.io/hikka.jpg")
    slug: str = Field(example="hikka-inc-123456")
    name: str = Field(example="Hikka Inc.")


class UserResponse(CustomModel):
    reference: str = Field(example="c773d0bf-1c42-4c18-aec8-1bdd8cb0a434")
    description: str | None = Field(example="Hikka")
    created: datetime = Field(example=1686088809)
    username: str | None = Field(example="hikka")
    avatar: str
