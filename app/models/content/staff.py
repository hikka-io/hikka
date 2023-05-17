from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from ..base import Base


class AnimeStaff(Base):
    __tablename__ = "service_content_anime_staff"

    role: Mapped[str]

    person_id = mapped_column(ForeignKey("service_content_people.id"))
    anime_id = mapped_column(ForeignKey("service_content_anime.id"))

    person: Mapped["Person"] = relationship(
        back_populates="staff_roles", foreign_keys=[person_id]
    )

    anime: Mapped["Anime"] = relationship(
        back_populates="staff", foreign_keys=[anime_id]
    )

    unique_constraint = UniqueConstraint(person_id, anime_id)


class AnimeVoice(Base):
    __tablename__ = "service_content_anime_voices"

    role: Mapped[str]

    character_id = mapped_column(ForeignKey("service_content_characters.id"))
    person_id = mapped_column(ForeignKey("service_content_people.id"))
    anime_id = mapped_column(ForeignKey("service_content_anime.id"))

    character: Mapped["Character"] = relationship(
        back_populates="voices", foreign_keys=[character_id]
    )

    person: Mapped["Person"] = relationship(
        back_populates="voice_roles", foreign_keys=[person_id]
    )

    anime: Mapped["Anime"] = relationship(
        back_populates="voices", foreign_keys=[anime_id]
    )

    unique_constraint = UniqueConstraint(character_id, person_id, anime_id)
