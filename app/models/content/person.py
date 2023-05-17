from ..mixins import ContentMixin, SlugMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import String
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

    # ToDo: initialized

    # ToDo: image
