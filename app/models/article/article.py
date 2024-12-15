from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from ..base import Base

from ..mixins import (
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
    SlugMixin,
):
    __tablename__ = "service_articles"

    category: Mapped[str] = mapped_column(String(32), index=True)
    tags: Mapped[list] = mapped_column(JSONB, default=[])
    draft: Mapped[bool] = mapped_column(default=True)
    title: Mapped[str] = mapped_column(String(255))
    vote_score: Mapped[int]
    text: Mapped[str]

    author_id = mapped_column(ForeignKey("service_users.id"))
    author: Mapped["User"] = relationship(foreign_keys=[author_id])

    # TODO: cascade delete
    content = relationship("ArticleContent", back_populates="article")

    cover_image_id = mapped_column(
        ForeignKey("service_images.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    cover_image_relation: Mapped["Image"] = relationship(
        foreign_keys=[cover_image_id], lazy="joined"
    )

    @hybrid_property
    def cover(self):
        if not self.cover_image_relation:
            return None

        if (
            self.cover_image_relation.ignore
            or not self.cover_image_relation.uploaded
        ):
            return None

        return self.cover_image_relation.url
