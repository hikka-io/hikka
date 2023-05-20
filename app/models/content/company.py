from ..association import anime_producers_association_table
from ..association import anime_studios_association_table
from ..mixins import ContentMixin, SlugMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import String
from datetime import datetime
from ..base import Base


class Company(Base, ContentMixin, SlugMixin):
    __tablename__ = "service_content_companies"

    name: Mapped[str] = mapped_column(String(255), nullable=True)

    favorites: Mapped[int] = mapped_column(default=0, nullable=True)
    updated: Mapped[datetime]

    producer_anime: Mapped[list["Anime"]] = relationship(
        secondary=anime_producers_association_table, back_populates="producers"
    )

    studio_anime: Mapped[list["Anime"]] = relationship(
        secondary=anime_studios_association_table, back_populates="studios"
    )

    # ToDo: image
