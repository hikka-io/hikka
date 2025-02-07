from ..association import novel_magazines_association_table
from ..association import genres_novel_association_table
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


class Novel(
    Base,
    SlugMixin,
    ContentMixin,
    UpdatedMixin,
    DeletedMixin,
    SynonymsMixin,
    IgnoredFieldsMixin,
    NeedsSearchUpdateMixin,
):
    __tablename__ = "service_content_novel"

    favourite_created: Mapped[datetime] = query_expression()

    comments_count: Mapped[int] = mapped_column(default=0)

    # Multilang fields
    title_original: Mapped[str] = mapped_column(nullable=True)
    synopsis_en: Mapped[str] = mapped_column(nullable=True)
    synopsis_ua: Mapped[str] = mapped_column(nullable=True)
    title_en: Mapped[str] = mapped_column(nullable=True)
    title_ua: Mapped[str] = mapped_column(nullable=True)

    # Service fields
    aggregator_updated: Mapped[datetime] = mapped_column(nullable=True)
    mal_id: Mapped[int] = mapped_column(index=True, nullable=True)
    translated_ua: Mapped[bool] = mapped_column(default=False)
    needs_update: Mapped[bool] = mapped_column(default=False)

    # Metadata
    status: Mapped[str] = mapped_column(String(16), index=True, nullable=True)
    year: Mapped[int] = mapped_column(index=True, nullable=True)
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

    genres: Mapped[list["Genre"]] = relationship(
        secondary=genres_novel_association_table,
        back_populates="novel",
    )

    authors: Mapped[list["NovelAuthor"]] = relationship(
        back_populates="novel",
        viewonly=True,
    )

    characters: Mapped[list["NovelCharacter"]] = relationship(
        back_populates="novel",
        viewonly=True,
    )

    magazines: Mapped[list["Magazine"]] = relationship(
        secondary=novel_magazines_association_table,
        back_populates="novel",
    )

    image_id = mapped_column(
        ForeignKey("service_images.id", ondelete="SET NULL"), index=True
    )

    image_relation: Mapped["Image"] = relationship(lazy="joined")

    franchise_id = mapped_column(
        ForeignKey("service_content_franchises.id", ondelete="SET NULL"),
        index=True,
    )

    franchise_relation: Mapped["Franchise"] = relationship(
        back_populates="novel", foreign_keys=[franchise_id]
    )

    read: Mapped[list["NovelRead"]] = relationship(
        primaryjoin="Novel.id == NovelRead.content_id",
        foreign_keys="[NovelRead.content_id]",
        viewonly=True,
    )

    @hybrid_property
    def image(self):
        if not self.image_relation:
            return None

        if self.image_relation.ignore or not self.image_relation.uploaded:
            return None

        return self.image_relation.url

    @hybrid_property
    def has_franchise(self):
        return self.franchise_id is not None

    @hybrid_property
    def data_type(self):
        return "novel"
