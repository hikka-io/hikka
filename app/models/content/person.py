from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from ..base import Base

from ..mixins import (
    NeedsSearchUpdateMixin,
    FavoritesMixin,
    SynonymsMixin,
    ContentMixin,
    UpdatedMixin,
    SlugMixin,
)


class Person(
    Base,
    SlugMixin,
    ContentMixin,
    UpdatedMixin,
    SynonymsMixin,
    FavoritesMixin,
    NeedsSearchUpdateMixin,
):
    __tablename__ = "service_content_people"

    needs_count_update: Mapped[bool] = mapped_column(default=True)
    characters_count: Mapped[bool] = mapped_column(default=True)
    anime_count: Mapped[int] = mapped_column(default=0)
    manga_count: Mapped[int] = mapped_column(default=0)
    novel_count: Mapped[int] = mapped_column(default=0)

    description_ua: Mapped[str] = mapped_column(nullable=True)
    name_native: Mapped[str] = mapped_column(nullable=True)
    name_en: Mapped[str] = mapped_column(nullable=True)
    name_ua: Mapped[str] = mapped_column(nullable=True)

    manga_author_roles: Mapped[list["MangaAuthor"]] = relationship(
        back_populates="person", viewonly=True
    )

    novel_author_roles: Mapped[list["NovelAuthor"]] = relationship(
        back_populates="person", viewonly=True
    )

    staff_roles: Mapped[list["AnimeStaff"]] = relationship(
        back_populates="person", viewonly=True
    )

    voice_roles: Mapped[list["AnimeVoice"]] = relationship(
        back_populates="person", viewonly=True
    )

    image_id = mapped_column(
        ForeignKey("service_images.id", ondelete="SET NULL"), index=True
    )

    image_relation: Mapped["Image"] = relationship(lazy="joined")

    @hybrid_property
    def image(self):
        if not self.image_relation:
            return None

        if self.image_relation.ignore or not self.image_relation.uploaded:
            return None

        return self.image_relation.url

    @hybrid_property
    def data_type(self):
        return "person"
