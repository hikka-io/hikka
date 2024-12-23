from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import ForeignKey, String, Index
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
    __table_args__ = (
        Index(
            "idx_article_tags_gin",
            "tags",
            postgresql_using="gin",
        ),
    )

    comments_count: Mapped[int] = mapped_column(default=0)

    category: Mapped[str] = mapped_column(String(32), index=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String))
    draft: Mapped[bool] = mapped_column(default=True)
    title: Mapped[str] = mapped_column(String(255))
    vote_score: Mapped[int]
    text: Mapped[str]

    author_id = mapped_column(ForeignKey("service_users.id"))
    author: Mapped["User"] = relationship(foreign_keys=[author_id])

    content_type: Mapped[str] = mapped_column(index=True, nullable=True)
    content_id: Mapped[UUID] = mapped_column(index=True, nullable=True)

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
