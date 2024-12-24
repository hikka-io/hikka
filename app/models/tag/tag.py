from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from ..base import Base
from uuid import UUID

from ..mixins import (
    CreatedMixin,
    UpdatedMixin,
)


class Tag(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "service_tags"
    __mapper_args__ = {
        "polymorphic_identity": "default",
        "polymorphic_on": "content_type",
    }

    content_count: Mapped[int] = mapped_column(default=0, index=True)
    name: Mapped[str] = mapped_column(index=True)
    content_type: Mapped[str]
    content_id: Mapped[UUID]


class ArticleTag(Tag):
    __mapper_args__ = {"polymorphic_identity": "article"}

    content_id = mapped_column(
        ForeignKey("service_articles.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Article"] = relationship(
        primaryjoin="Article.id == ArticleTag.content_id",
        foreign_keys=[content_id],
    )
