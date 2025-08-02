from enum import Enum

from pydantic import Field, field_validator

from app import constants
from app.schemas import CustomModel


# Enums
class MALContentTypeEnum(str, Enum):
    content_anime = constants.CONTENT_ANIME
    content_manga = constants.CONTENT_MANGA
    content_novel = constants.CONTENT_NOVEL


# Args
class MALAnimeArgs(CustomModel):
    mal_ids: list[int] = Field(min_length=1, max_length=500)

    @field_validator("mal_ids")
    def validate_mal_id(cls, mal_ids):
        if len(list(set(mal_ids))) != len(mal_ids):
            raise ValueError("Duplicated mal_id")

        return mal_ids
