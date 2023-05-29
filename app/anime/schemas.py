from app.schemas import ORJSONModel
from datetime import datetime
from typing import Union


# Responses
class GenreResponse(ORJSONModel):
    name_en: Union[str, None]
    name_ua: Union[str, None]
    slug: str


class CompanyResponse(ORJSONModel):
    name: str
    slug: str


class AnimeInfoResponse(ORJSONModel):
    producers: list[CompanyResponse]
    studios: list[CompanyResponse]
    genres: list[GenreResponse]

    start_date: Union[datetime, None]
    end_date: Union[datetime, None]

    total_episodes: Union[int, None]
    synopsis_en: Union[str, None]
    synopsis_ua: Union[str, None]
    media_type: Union[str, None]
    franchise: Union[str, None]
    title_ua: Union[str, None]
    title_en: Union[str, None]
    title_ja: Union[str, None]
    episodes: Union[int, None]
    duration: Union[int, None]
    poster: Union[str, None]
    status: Union[str, None]
    source: Union[str, None]
    rating: Union[str, None]
    scored_by: int
    score: float
    nsfw: bool
    slug: str

    synonyms: list[str]
    external: list[dict]
    videos: list[dict]
    ost: list[dict]
    stats: dict
