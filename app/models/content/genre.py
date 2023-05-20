from ..association import anime_genres_association_table
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from ..mixins import ContentMixin
from sqlalchemy import String
from ..base import Base


class GenreMixin:
    name_en: Mapped[str] = mapped_column(String(64), nullable=True)
    name_ua: Mapped[str] = mapped_column(String(64), nullable=True)

    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    type: Mapped[str] = mapped_column(String(32))


class AnimeGenre(Base, GenreMixin, ContentMixin):
    __tablename__ = "service_content_anime_genres"

    anime: Mapped[list["Anime"]] = relationship(
        secondary=anime_genres_association_table, back_populates="genres"
    )
