from ..association import tags_articles_association_table
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from ..base import Base
from uuid import UUID

from ..mixins import (
    MyScoreMixin,
    CreatedMixin,
    UpdatedMixin,
    DeletedMixin,
    SlugMixin,
)


class Article(
    Base,
    CreatedMixin,
    UpdatedMixin,
    DeletedMixin,
    MyScoreMixin,
    SlugMixin,
):
    __tablename__ = "service_articles"

    comments_count: Mapped[int] = mapped_column(default=0)

    category: Mapped[str] = mapped_column(String(32), index=True)
    draft: Mapped[bool] = mapped_column(default=True)
    title: Mapped[str] = mapped_column(String(255))
    vote_score: Mapped[int]
    text: Mapped[str]

    author_id = mapped_column(ForeignKey("service_users.id"))
    author: Mapped["User"] = relationship(foreign_keys=[author_id])

    content_type: Mapped[str] = mapped_column(index=True, nullable=True)
    content_id: Mapped[UUID] = mapped_column(index=True, nullable=True)

    tags: Mapped[list["ArticleTag"]] = relationship(
        secondary=tags_articles_association_table,
        back_populates="articles",
        lazy="joined",
    )

    cover_image_id = mapped_column(
        ForeignKey("service_images.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    cover_image: Mapped["Image"] = relationship(
        foreign_keys=[cover_image_id], lazy="joined"
    )

    @hybrid_property
    def cover(self):
        if not self.cover_image:
            return None

        if self.cover_image.ignore or not self.cover_image.uploaded:
            return None

        return self.cover_image.url

    @hybrid_property
    def data_type(self):
        return "article"
