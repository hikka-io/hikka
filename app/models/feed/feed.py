from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from ..base import Base
from uuid import UUID

from ..mixins import (
    CreatedMixin,
    DeletedMixin,
)


class Feed(
    Base,
    CreatedMixin,
    DeletedMixin,
):
    __tablename__ = "service_feed"
    __table_args__ = (Index("ix_feed_content", "content_type", "content_id"),)

    content_type: Mapped[str]
    content_id: Mapped[UUID]

    author_id = mapped_column(ForeignKey("service_users.id"))
    user_id = mapped_column(ForeignKey("service_users.id"))

    author: Mapped["User"] = relationship(foreign_keys=[author_id])
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
