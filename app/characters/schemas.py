from app.schemas import ORJSONModel, PaginationResponse
from pydantic import constr
from pydantic import Field
from typing import Union


# Args
class CharactersSearchArgs(ORJSONModel):
    query: Union[constr(min_length=3, max_length=255), None] = None
    page: int = Field(default=1, gt=0)


# Responses
class CharacterResponse(ORJSONModel):
    name_ua: Union[str, None]
    name_en: Union[str, None]
    name_ja: Union[str, None]
    image: Union[str, None]


class CharactersSearchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[CharacterResponse]
