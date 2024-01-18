from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from ..base import Base

from ..mixins import (
    NeedsSearchUpdateMixin,
    FavoritesMixin,
    ContentMixin,
    UpdatedMixin,
    SlugMixin,
)


class Company(
    Base,
    FavoritesMixin,
    ContentMixin,
    UpdatedMixin,
    SlugMixin,
    NeedsSearchUpdateMixin,
):
    __tablename__ = "service_content_companies"

    name: Mapped[str] = mapped_column(nullable=True)

    anime: Mapped[list["CompanyAnime"]] = relationship(
        back_populates="company", viewonly=True
    )

    image_id = mapped_column(
        ForeignKey("service_images.id", ondelete="SET NULL"), index=True
    )

    image_relation: Mapped["Image"] = relationship(lazy="selectin")

    produced_anime: Mapped[list["Anime"]] = relationship(
        secondary="service_content_companies_anime",
        back_populates="producers",
        viewonly=True,
    )

    @hybrid_property
    def image(self):
        if not self.image_relation:
            return None

        if self.image_relation.ignore or not self.image_relation.uploaded:
            return None

        return self.image_relation.url


class CompanyAnime(Base):
    __tablename__ = "service_content_companies_anime"

    type: Mapped[str] = mapped_column(String(32), index=True)
    company_id = mapped_column(ForeignKey("service_content_companies.id"))
    anime_id = mapped_column(ForeignKey("service_content_anime.id"))

    company: Mapped["Company"] = relationship(
        back_populates="anime", foreign_keys=[company_id]
    )

    anime: Mapped["Anime"] = relationship(
        back_populates="companies", foreign_keys=[anime_id]
    )

    unique_constraint = UniqueConstraint(company_id, anime_id, type)
