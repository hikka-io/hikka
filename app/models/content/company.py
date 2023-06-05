# from ..association import anime_producers_association_table
# from ..association import anime_studios_association_table
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from ..mixins import ContentMixin, SlugMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from datetime import datetime
from ..base import Base


class Company(Base, ContentMixin, SlugMixin):
    __tablename__ = "service_content_companies"

    name: Mapped[str] = mapped_column(String(255), nullable=True)

    favorites: Mapped[int] = mapped_column(default=0, nullable=True)
    updated: Mapped[datetime]

    anime: Mapped[list["CompanyAnime"]] = relationship(back_populates="company")

    image_id = mapped_column(
        ForeignKey("service_images.id", ondelete="SET NULL")
    )

    image_relation: Mapped["Image"] = relationship(lazy="selectin")

    @hybrid_property
    def image(self):
        return self.image_relation.url if self.image_relation else None


class CompanyAnime(Base):
    __tablename__ = "service_content_companies_anime"

    type: Mapped[str] = mapped_column(String(32))

    company_id = mapped_column(ForeignKey("service_content_companies.id"))
    anime_id = mapped_column(ForeignKey("service_content_anime.id"))

    company: Mapped["Company"] = relationship(
        back_populates="anime", foreign_keys=[company_id]
    )

    anime: Mapped["Anime"] = relationship(
        back_populates="companies", foreign_keys=[anime_id]
    )

    unique_constraint = UniqueConstraint(company_id, anime_id, type)
