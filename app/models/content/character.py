from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from ..mixins import ContentMixin, SlugMixin
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
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

    voices: Mapped[list["AnimeVoice"]] = relationship(
        back_populates="character"
    )

    image_id = mapped_column(
        ForeignKey("service_images.id", ondelete="SET NULL")
    )

    image_relation: Mapped["Image"] = relationship(lazy="selectin")

    @hybrid_property
    def image(self):
        return self.image_relation.url if self.image_relation else None


class AnimeCharacter(Base):
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
