from app.schemas import CustomModel
from pydantic import Field
from app import constants
from enum import Enum


# Enums
class CompanyTypeEnum(str, Enum):
    producer = constants.COMPANY_ANIME_PRODUCER
    studio = constants.COMPANY_ANIME_STUDIO


# Responses
class CompanyResponse(CustomModel):
    image: str | None = Field(examples=["https://cdn.hikka.io/hikka.jpg"])
    slug: str = Field(examples=["hikka-inc-123456"])
    name: str = Field(examples=["Hikka Inc."])
