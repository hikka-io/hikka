from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from ..base import Base
from uuid import UUID

from ..mixins import (
    CreatedMixin,
    UpdatedMixin,
)


class Feed(
    Base,
    CreatedMixin,
    UpdatedMixin,
):
    __tablename__ = "service_feed"

    deleted: Mapped[bool] = mapped_column(default=False)
    content_type: Mapped[str]
    content_id: Mapped[UUID]

    user_id = mapped_column(ForeignKey("service_users.id"))
