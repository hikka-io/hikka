from pydantic import BaseModel, Field
from app.constants import SEASON
from typing import Union


class AnimeSearchArgs(BaseModel):
    # season: Union[str, None] = Field(default=None, regex="|".join(SEASON))
    # sort: list[str] = Field(default=["score:desc", "scored_by:desc"])
    # year: list[Union[int, None], Union[int, None]] = [None, None]
    # query: Union[str, None] = Field(default=None)
    # page: int = Field(default=1, gt=0)
    # producers: list[str] = []
    # studios: list[str] = []
    # release: list[str] = []
    # genres: list[str] = []
    # rating: list[str] = []
    # source: list[str] = []
    status: list[str] = []
