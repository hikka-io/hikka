from ..association import manga_magazines_association_table
from ..association import manga_genres_association_table
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import query_expression
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import String
from datetime import datetime
from ..base import Base

from ..mixins import (
    NeedsSearchUpdateMixin,
    IgnoredFieldsMixin,
    SynonymsMixin,
    ContentMixin,
    UpdatedMixin,
    DeletedMixin,
    SlugMixin,
)


class Manga(
    Base,
    SlugMixin,
    ContentMixin,
    UpdatedMixin,
    DeletedMixin,
    SynonymsMixin,
    IgnoredFieldsMixin,
    NeedsSearchUpdateMixin,
):
    __tablename__ = "service_content_manga"

    favourite_created: Mapped[datetime] = query_expression()
    comments_count: Mapped[int] = query_expression()

    # Multilang fields
    title_original: Mapped[str] = mapped_column(String(255), nullable=True)
    title_en: Mapped[str] = mapped_column(String(255), nullable=True)
    title_ua: Mapped[str] = mapped_column(String(255), nullable=True)
    synopsis_en: Mapped[str] = mapped_column(nullable=True)
    synopsis_ua: Mapped[str] = mapped_column(nullable=True)

    # Service fields
    aggregator_updated: Mapped[datetime] = mapped_column(nullable=True)
    mal_id: Mapped[int] = mapped_column(index=True, nullable=True)
    translated_ua: Mapped[bool] = mapped_column(default=False)
    needs_update: Mapped[bool] = mapped_column(default=False)

    # Metadata
    status: Mapped[str] = mapped_column(String(16), index=True, nullable=True)
    start_date: Mapped[datetime] = mapped_column(nullable=True)
    end_date: Mapped[datetime] = mapped_column(nullable=True)
    chapters: Mapped[int] = mapped_column(nullable=True)
    volumes: Mapped[int] = mapped_column(nullable=True)
    nsfw: Mapped[bool] = mapped_column(nullable=True)
    scored_by: Mapped[int] = mapped_column(default=0)
    score: Mapped[float] = mapped_column(default=0)
    media_type: Mapped[str] = mapped_column(
        String(16), index=True, nullable=True
    )

    external: Mapped[list] = mapped_column(JSONB, default=[])
    stats: Mapped[list] = mapped_column(JSONB, default=[])

    genres: Mapped[list["MangaGenre"]] = relationship(
        secondary=manga_genres_association_table,
        back_populates="manga",
    )

    authors: Mapped[list["MangaAuthor"]] = relationship(
        back_populates="manga",
    )

    characters: Mapped[list["MangaCharacter"]] = relationship(
        back_populates="manga",
        viewonly=True,
    )

    magazines: Mapped[list["Magazine"]] = relationship(
        secondary=manga_magazines_association_table,
        back_populates="manga",
    )

    poster_id = mapped_column(
        ForeignKey("service_images.id", ondelete="SET NULL"), index=True
    )

    image_relation: Mapped["Image"] = relationship(lazy="joined")

    @hybrid_property
    def image(self):
        if not self.image_relation:
            return None

        if self.image_relation.ignore or not self.image_relation.uploaded:
            return None

        return self.image_relation.url

    @hybrid_property
    def data_type(self):
        return "manga"
