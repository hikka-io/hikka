from ..association import anime_staff_roles_association_table
from sqlalchemy import ForeignKey, UniqueConstraint, String
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from ..mixins import SlugMixin
from sqlalchemy import desc
from ..base import Base


class AnimeStaffRole(Base, SlugMixin):
    __tablename__ = "service_content_anime_staff_roles"

    name_en: Mapped[str] = mapped_column(nullable=True)
    name_ua: Mapped[str] = mapped_column(nullable=True)
    weight: Mapped[int] = mapped_column(nullable=True)

    staff: Mapped[list["AnimeStaff"]] = relationship(
        secondary=anime_staff_roles_association_table,
        back_populates="roles",
        viewonly=True,
    )


class AnimeStaff(Base):
    __tablename__ = "service_content_anime_staff"

    weight: Mapped[int] = mapped_column(nullable=True)

    roles: Mapped[list["AnimeStaffRole"]] = relationship(
        secondary=anime_staff_roles_association_table,
        order_by="AnimeStaffRole.weight.desc()",
        back_populates="staff",
        lazy="selectin",
    )

    person_id = mapped_column(
        ForeignKey("service_content_people.id"),
        index=True,
    )

    anime_id = mapped_column(
        ForeignKey("service_content_anime.id"),
        index=True,
    )

    person: Mapped["Person"] = relationship(
        back_populates="staff_roles", foreign_keys=[person_id]
    )

    anime: Mapped["Anime"] = relationship(
        back_populates="staff", foreign_keys=[anime_id]
    )

    unique_constraint = UniqueConstraint(person_id, anime_id)


class AnimeVoice(Base):
    __tablename__ = "service_content_anime_voices"

    language: Mapped[str] = mapped_column(String(32), index=True)

    character_id = mapped_column(
        ForeignKey("service_content_characters.id"),
        index=True,
    )

    person_id = mapped_column(
        ForeignKey("service_content_people.id"),
        index=True,
    )

    anime_id = mapped_column(
        ForeignKey("service_content_anime.id"),
        index=True,
    )

    character: Mapped["Character"] = relationship(
        back_populates="voices", foreign_keys=[character_id]
    )

    person: Mapped["Person"] = relationship(
        back_populates="voice_roles", foreign_keys=[person_id]
    )

    anime: Mapped["Anime"] = relationship(
        back_populates="voices", foreign_keys=[anime_id]
    )
