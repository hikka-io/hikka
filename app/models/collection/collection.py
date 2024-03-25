from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import query_expression
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import String
from datetime import datetime
from ..base import Base

from ..mixins import (
    CreatedMixin,
    UpdatedMixin,
)


class Collection(
    Base,
    CreatedMixin,
    UpdatedMixin,
):
    __tablename__ = "service_collections"

    # ToDo: moderated
    favourite_created: Mapped[datetime] = query_expression()
    comments_count: Mapped[int] = query_expression()
    my_score: Mapped[int] = query_expression()

    system_ranking: Mapped[float] = mapped_column(index=True, default=0)
    visibility: Mapped[str] = mapped_column(String(16), index=True)
    labels_order: Mapped[list[str]] = mapped_column(ARRAY(String))
    description: Mapped[str] = mapped_column(nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String))
    content_type: Mapped[str] = mapped_column(index=True)
    spoiler: Mapped[bool] = mapped_column(default=False)
    nsfw: Mapped[bool] = mapped_column(default=False)
    title: Mapped[str] = mapped_column(String(255))
    vote_score: Mapped[int]
    deleted: Mapped[bool]
    private: Mapped[bool]
    entries: Mapped[int]

    author_id = mapped_column(ForeignKey("service_users.id"))
    author: Mapped["User"] = relationship(
        foreign_keys=[author_id],
        lazy="selectin",
    )

    collection: Mapped[list["CollectionContent"]] = relationship(
        foreign_keys="[CollectionContent.collection_id]",
        back_populates="collection",
    )

    @hybrid_property
    def slug(self):
        return str(self.reference)
