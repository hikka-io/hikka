from sqlalchemy import ForeignKey, UniqueConstraint
from ..mixins import ContentMixin, SlugMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import String
from datetime import datetime
from ..base import Base


class Character(Base, ContentMixin, SlugMixin):
    __tablename__ = "service_content_characters"

    name_ja: Mapped[str] = mapped_column(String(255), nullable=True)
    name_en: Mapped[str] = mapped_column(String(255), nullable=True)
    name_ua: Mapped[str] = mapped_column(String(255), nullable=True)

    favorites: Mapped[int] = mapped_column(default=0, nullable=True)
    updated: Mapped[datetime]

    anime_roles: Mapped[list["AnimeCharacter"]] = relationship(
        back_populates="character"
    )

    voices: Mapped[list["AnimeVoices"]] = relationship(
        back_populates="character"
    )


class AnimeCharacter(Base, SlugMixin):
    __tablename__ = "service_content_anime_characters"

    main: Mapped[bool]

    character_id = mapped_column(ForeignKey("service_content_characters.id"))
    anime_id = mapped_column(ForeignKey("service_content_anime.id"))

    character: Mapped["Character"] = relationship(
        back_populates="anime_roles", foreign_keys=[character_id]
    )

    anime: Mapped["Anime"] = relationship(
        back_populates="characters", foreign_keys=[anime_id]
    )

    unique_constraint = UniqueConstraint(character_id, anime_id)
