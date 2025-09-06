from ..association import tags_articles_association_table
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from ..base import Base
from uuid import UUID

from ..mixins import (
    CommentContentMixin,
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
    CommentContentMixin,
    SlugMixin,
):
    __tablename__ = "service_articles"

    # In community we trust (but it's nice to have some control)
    trusted: Mapped[bool] = mapped_column(default=False)

    category: Mapped[str] = mapped_column(String(32), index=True)
    document: Mapped[list] = mapped_column(JSONB, default=[])
    draft: Mapped[bool] = mapped_column(default=True)
    title: Mapped[str] = mapped_column(String(255))
    views: Mapped[int] = mapped_column(default=0)
    vote_score: Mapped[int]

    author_id = mapped_column(ForeignKey("service_users.id"))
    author: Mapped["User"] = relationship(foreign_keys=[author_id])

    content_type: Mapped[str] = mapped_column(index=True, nullable=True)
    content_id: Mapped[UUID] = mapped_column(index=True, nullable=True)

    tags: Mapped[list["ArticleTag"]] = relationship(
        secondary=tags_articles_association_table,
        back_populates="articles",
        lazy="joined",
    )

    @hybrid_property
    def data_type(self):
        return "article"
