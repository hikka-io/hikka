from pydantic import Field, HttpUrl
from app.schemas import ORJSONModel
from typing import Union, Optional
from app import constants
from enum import Enum


class AnimeExternal(ORJSONModel):
    url: HttpUrl = Field(example="https://demonslayer-anime.com/mugentrainarc/")
    text: str = Field(example="Official Site", max_length=255)


class AnimeVideoTypeEnum(str, Enum):
    video_promo = constants.VIDEO_PROMO
    video_music = constants.VIDEO_MUSIC


class AnimeVideo(ORJSONModel):
    url: HttpUrl = Field(example="https://youtu.be/_4W1OQoDEDg")
    title: Union[str, None] = Field(
        example="ED 2 (Artist ver.)", max_length=255
    )
    description: Union[str, None] = Field(example="...")
    video_type: AnimeVideoTypeEnum = Field(example="video_music")


class AnimeOSTTypeEnum(str, Enum):
    opening = constants.OST_OPENING
    ending = constants.OST_ENDING


class AnimeOST(ORJSONModel):
    # ToDo: Some more sanity checks like making sure that the indexes are in
    # the correct order
    index: int = Field(example=1)
    title: Union[str, None] = Field(example="fantastic dreamer", max_length=255)
    author: Union[str, None] = Field(example="Machico", max_length=255)
    spotify: Union[HttpUrl, None] = Field(
        example="https://open.spotify.com/track/3BIhcWQV2hGRoEXdLL3Fzw"
    )
    ost_type: AnimeOSTTypeEnum = Field(example="opening")


class EditAnimeArgs(ORJSONModel):
    title_ja: Optional[str] = Field(
        example="Kimetsu no Yaiba: Mugen Ressha-hen", max_length=255
    )
    title_en: Optional[str] = Field(
        example="Demon Slayer: Kimetsu no Yaiba Mugen Train Arc", max_length=255
    )
    title_ua: Union[str, None] = Field(
        example="Клинок, який знищує демонів: Арка Нескінченного потяга",
        max_length=255,
    )
    synopsis_en: Union[str, None] = Field(example="...")
    synopsis_ua: Union[str, None] = Field(example="...")

    synonyms: Union[list[str], None] = Field()
    # external: Union[list[AnimeExternal], None] = Field()
    # videos: Union[list[AnimeVideo], None] = Field()
    # ost: Union[list[AnimeOST], None] = Field()

    # poster: Union[HttpUrl, None] = Field()

    description: Union[str, None] = Field(example="...")
