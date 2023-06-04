from ..association import anime_producers_association_table
from ..association import anime_studios_association_table
from sqlalchemy.ext.hybrid import hybrid_property
from ..mixins import ContentMixin, SlugMixin
from sqlalchemy import ForeignKey, String
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

    producer_anime: Mapped[list["Anime"]] = relationship(
        secondary=anime_producers_association_table, back_populates="producers"
    )

    studio_anime: Mapped[list["Anime"]] = relationship(
        secondary=anime_studios_association_table, back_populates="studios"
    )

    image_id = mapped_column(
        ForeignKey("service_images.id", ondelete="SET NULL")
    )

    image_relation: Mapped["Image"] = relationship(lazy="selectin")

    @hybrid_property
    def image(self):
        return self.image_relation.url if self.image_relation else None

    # ToDo: image
