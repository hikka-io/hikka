from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from ..base import Base

from ..mixins import (
    FavoritesMixin,
    ContentMixin,
    UpdatedMixin,
    SlugMixin,
)


class Person(
    Base,
    FavoritesMixin,
    ContentMixin,
    UpdatedMixin,
    SlugMixin,
):
    __tablename__ = "service_content_people"

    name_native: Mapped[str] = mapped_column(nullable=True)
    name_en: Mapped[str] = mapped_column(nullable=True)
    name_ua: Mapped[str] = mapped_column(nullable=True)

    staff_roles: Mapped[list["AnimeStaff"]] = relationship(
        back_populates="person"
    )

    voice_roles: Mapped[list["AnimeVoice"]] = relationship(
        back_populates="person", viewonly=True
    )

    image_id = mapped_column(
        ForeignKey("service_images.id", ondelete="SET NULL"), index=True
    )

    image_relation: Mapped["Image"] = relationship(lazy="selectin")

    @hybrid_property
    def image(self):
        if not self.image_relation:
            return None

        if self.image_relation.ignore or not self.image_relation.uploaded:
            return None

        return self.image_relation.url
