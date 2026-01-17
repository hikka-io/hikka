from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import query_expression
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from datetime import datetime
from ..base import Base

from ..mixins import (
    NeedsSearchUpdateMixin,
    CommentContentMixin,
    FavoritesMixin,
    SynonymsMixin,
    ContentMixin,
    UpdatedMixin,
    NamesMixin,
    SlugMixin,
)


class Character(
    Base,
    SlugMixin,
    NamesMixin,
    ContentMixin,
    UpdatedMixin,
    SynonymsMixin,
    FavoritesMixin,
    CommentContentMixin,
    NeedsSearchUpdateMixin,
):
    __tablename__ = "service_content_characters"

    needs_count_update: Mapped[bool] = mapped_column(default=True)
    voices_count: Mapped[int] = mapped_column(default=0)
    anime_count: Mapped[int] = mapped_column(default=0)
    manga_count: Mapped[int] = mapped_column(default=0)
    novel_count: Mapped[int] = mapped_column(default=0)

    favourite_created: Mapped[datetime] = query_expression()

    description_ua: Mapped[str] = mapped_column(nullable=True)

    image_id = mapped_column(
        ForeignKey("service_images.id", ondelete="SET NULL"), index=True
    )

    image_relation: Mapped["Image"] = relationship(lazy="joined")

    anime: Mapped[list["AnimeCharacter"]] = relationship(
        back_populates="character", viewonly=True
    )

    manga: Mapped[list["MangaCharacter"]] = relationship(
        back_populates="character", viewonly=True
    )

    novel: Mapped[list["NovelCharacter"]] = relationship(
        back_populates="character", viewonly=True
    )

    voices: Mapped[list["AnimeVoice"]] = relationship(
        back_populates="character", viewonly=True
    )

    @hybrid_property
    def image(self):
        if not self.image_relation:
            return None

        if self.image_relation.ignore or not self.image_relation.uploaded:
            return None

        return self.image_relation.url

    @hybrid_property
    def data_type(self):
        return "character"


class AnimeCharacter(Base):
    __tablename__ = "service_content_anime_characters"

    main: Mapped[bool]

    character_id = mapped_column(
        ForeignKey("service_content_characters.id"),
        index=True,
    )

    anime_id = mapped_column(
        ForeignKey("service_content_anime.id"),
        index=True,
    )

    character: Mapped["Character"] = relationship(
        back_populates="anime", foreign_keys=[character_id]
    )

    anime: Mapped["Anime"] = relationship(
        back_populates="characters", foreign_keys=[anime_id]
    )

    unique_constraint = UniqueConstraint(character_id, anime_id)


class MangaCharacter(Base):
    __tablename__ = "service_content_manga_characters"

    main: Mapped[bool]

    character_id = mapped_column(
        ForeignKey("service_content_characters.id"),
        index=True,
    )

    manga_id = mapped_column(
        ForeignKey("service_content_manga.id"),
        index=True,
    )

    character: Mapped["Character"] = relationship(
        back_populates="manga", foreign_keys=[character_id]
    )

    manga: Mapped["Manga"] = relationship(
        back_populates="characters", foreign_keys=[manga_id]
    )

    unique_constraint = UniqueConstraint(character_id, manga_id)


class NovelCharacter(Base):
    __tablename__ = "service_content_novel_characters"

    main: Mapped[bool]

    character_id = mapped_column(
        ForeignKey("service_content_characters.id"),
        index=True,
    )

    novel_id = mapped_column(
        ForeignKey("service_content_novel.id"),
        index=True,
    )

    character: Mapped["Character"] = relationship(
        back_populates="novel", foreign_keys=[character_id]
    )

    novel: Mapped["Novel"] = relationship(
        back_populates="characters", foreign_keys=[novel_id]
    )

    unique_constraint = UniqueConstraint(character_id, novel_id)
