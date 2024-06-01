from ..association import anime_genres_association_table
from ..association import manga_genres_association_table
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import String
from ..base import Base

from ..mixins import (
    ContentMixin,
    SlugMixin,
)


class AnimeGenre(Base, ContentMixin, SlugMixin):
    __tablename__ = "service_content_anime_genres"

    name_en: Mapped[str] = mapped_column(String(64), nullable=True)
    name_ua: Mapped[str] = mapped_column(String(64), nullable=True)
    type: Mapped[str] = mapped_column(String(32), index=True)

    anime: Mapped[list["Anime"]] = relationship(
        secondary=anime_genres_association_table, back_populates="genres"
    )


class MangaGenre(Base, ContentMixin, SlugMixin):
    __tablename__ = "service_content_manga_genres"

    name_en: Mapped[str] = mapped_column(String(64), nullable=True)
    name_ua: Mapped[str] = mapped_column(String(64), nullable=True)
    type: Mapped[str] = mapped_column(String(32), index=True)

    manga: Mapped[list["Manga"]] = relationship(
        secondary=manga_genres_association_table, back_populates="genres"
    )
