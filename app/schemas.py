from pydantic import BaseModel, Extra, Field, constr
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from typing import Union
from . import constants
from enum import Enum
from . import utils
import orjson


# Dump dict using orjson
def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


# Custom Pydantic model
class ORJSONModel(BaseModel):
    class Config:
        json_encoders = {datetime: utils.to_timestamp}
        json_dumps = orjson_dumps
        json_loads = orjson.loads
        use_enum_values = True
        extra = Extra.forbid
        orm_mode = True

    def serializable_dict(self, **kwargs):
        default_dict = super().dict(**kwargs)
        return jsonable_encoder(default_dict)


# Enums
class CompanyTypeEnum(str, Enum):
    producer = constants.COMPANY_ANIME_PRODUCER
    studio = constants.COMPANY_ANIME_STUDIO


# Args
class PaginationArgs(ORJSONModel):
    page: int = Field(default=1, gt=0, example=1)


# Responses
class PaginationResponse(ORJSONModel):
    total: int = Field(example=20)
    pages: int = Field(example=2)
    page: int = Field(example=1)


class QuerySearchArgs(ORJSONModel):
    query: Union[constr(min_length=3, max_length=255), None] = None
    page: int = Field(default=1, gt=0, example=1)


class AnimeResponse(ORJSONModel):
    media_type: Union[str, None] = Field(example="tv")
    title_ua: Union[str, None] = Field(
        example="Цей прекрасний світ, благословенний Богом!"
    )
    title_en: Union[str, None] = Field(
        example="KonoSuba: God's Blessing on This Wonderful World!"
    )
    title_ja: Union[str, None] = Field(
        example="Kono Subarashii Sekai ni Shukufuku wo!"
    )
    episodes_released: Union[int, None] = Field(example="10")
    episodes_total: Union[int, None] = Field(example="10")
    poster: Union[str, None] = Field(example="https://cdn.hikka.io/hikka.jpg")
    status: Union[str, None] = Field(example="finished")
    scored_by: int = Field(example=1210150)
    score: float = Field(example=8.11)
    slug: str = Field(example="kono-subarashii-sekai-ni-shukufuku-wo-123456")
    season: Union[str, None]
    source: Union[str, None]
    rating: Union[str, None]
    year: Union[int, None]


class CharacterResponse(ORJSONModel):
    name_ua: Union[str, None] = Field(example="Меґумін")
    name_en: Union[str, None] = Field(example="Megumin")
    name_ja: Union[str, None] = Field(example="めぐみん")
    image: Union[str, None] = Field(example="https://cdn.hikka.io/hikka.jpg")
    slug: str = Field(example="megumin-123456")


class PersonResponse(ORJSONModel):
    name_native: Union[str, None] = Field(example="高橋 李依")
    name_ua: Union[str, None] = Field(example="Ріє Такахаші")
    name_en: Union[str, None] = Field(example="Rie Takahashi")
    image: Union[str, None] = Field(example="https://cdn.hikka.io/hikka.jpg")
    slug: str = Field(example="rie-takahashi-123456")


class AnimeFavouriteResponse(ORJSONModel):
    reference: str = Field(example="c773d0bf-1c42-4c18-aec8-1bdd8cb0a434")
    created: datetime = Field(example=1686088809)
    anime: AnimeResponse


class SuccessResponse(ORJSONModel):
    success: bool = Field(example=True)


class CompanyResponse(ORJSONModel):
    image: Union[str, None] = Field(example="https://cdn.hikka.io/hikka.jpg")
    slug: str = Field(example="hikka-inc-123456")
    name: str = Field(example="Hikka Inc.")
