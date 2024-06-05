from ..association import anime_genres_association_table_legacy
from ..association import manga_genres_association_table_legacy
from ..association import genres_anime_association_table
from ..association import genres_manga_association_table
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import String
from ..base import Base

from ..mixins import (
    ContentMixin,
    SlugMixin,
)


class Genre(Base, ContentMixin, SlugMixin):
    __tablename__ = "service_content_genres"

    name_en: Mapped[str] = mapped_column(String(64), nullable=True)
    name_ua: Mapped[str] = mapped_column(String(64), nullable=True)
    type: Mapped[str] = mapped_column(String(32), index=True)

    anime: Mapped[list["Anime"]] = relationship(
        secondary=genres_anime_association_table,
        back_populates="genres",
    )

    manga: Mapped[list["Manga"]] = relationship(
        secondary=genres_manga_association_table,
        back_populates="genres",
    )


class AnimeGenreLegacy(Base, ContentMixin, SlugMixin):
    __tablename__ = "service_content_anime_genres"

    name_en: Mapped[str] = mapped_column(String(64), nullable=True)
    name_ua: Mapped[str] = mapped_column(String(64), nullable=True)
    type: Mapped[str] = mapped_column(String(32), index=True)

    anime: Mapped[list["Anime"]] = relationship(
        secondary=anime_genres_association_table_legacy,
        back_populates="genres_legacy",
    )


class MangaGenreLegacy(Base, ContentMixin, SlugMixin):
    __tablename__ = "service_content_manga_genres"

    name_en: Mapped[str] = mapped_column(String(64), nullable=True)
    name_ua: Mapped[str] = mapped_column(String(64), nullable=True)
    type: Mapped[str] = mapped_column(String(32), index=True)

    manga: Mapped[list["Manga"]] = relationship(
        secondary=manga_genres_association_table_legacy,
        back_populates="genres_legacy",
    )
