from sqlalchemy.ext.hybrid import hybrid_property
from ..mixins import ContentMixin, SlugMixin
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from datetime import datetime
from ..base import Base


class Person(Base, ContentMixin, SlugMixin):
    __tablename__ = "service_content_people"

    name_native: Mapped[str] = mapped_column(String(255), nullable=True)
    name_en: Mapped[str] = mapped_column(String(255), nullable=True)
    name_ua: Mapped[str] = mapped_column(String(255), nullable=True)

    favorites: Mapped[int] = mapped_column(default=0, nullable=True)
    updated: Mapped[datetime]

    staff_roles: Mapped[list["AnimeStaff"]] = relationship(
        back_populates="person"
    )

    voice_roles: Mapped[list["AnimeVoice"]] = relationship(
        back_populates="person"
    )

    image_id = mapped_column(
        ForeignKey("service_images.id", ondelete="SET NULL")
    )

    image_relation: Mapped["Image"] = relationship(lazy="selectin")

    @hybrid_property
    def image(self):
        return self.image_relation.url if self.image_relation else None
