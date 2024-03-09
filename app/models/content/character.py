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
    FavoritesMixin,
    ContentMixin,
    UpdatedMixin,
    NamesMixin,
    SlugMixin,
)


class Character(
    Base,
    FavoritesMixin,
    ContentMixin,
    UpdatedMixin,
    NamesMixin,
    SlugMixin,
    NeedsSearchUpdateMixin,
):
    __tablename__ = "service_content_characters"

    favourite_created: Mapped[datetime] = query_expression()

    description_ua: Mapped[str] = mapped_column(nullable=True)

    image_id = mapped_column(
        ForeignKey("service_images.id", ondelete="SET NULL"), index=True
    )

    image_relation: Mapped["Image"] = relationship(lazy="selectin")

    anime: Mapped[list["AnimeCharacter"]] = relationship(
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
