from sqlalchemy import Enum, ForeignKey, String, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from ..base import Base
from uuid import UUID

from ..mixins import (
    CreatedMixin,
    UpdatedMixin,
)


# ToDo: move those to a separate location?
statuses = ("PENDING", "APPROVED", "DENIED", "CLOSED")
content_types = (
    "anime",
    "manga",
    "character",
    "company",
    "episode",
    "genre",
    "person",
    "staff",
)


class ContentEdit(
    Base,
    CreatedMixin,
    UpdatedMixin,
):
    __tablename__ = "service_edits"

    edit_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    status: Mapped[str] = mapped_column(Enum(*statuses, name="status"))
    description: Mapped[str] = mapped_column(String(140), nullable=True)
    hidden: Mapped[bool] = mapped_column(Boolean, default=False)

    content_id: Mapped[UUID]
    content_type: Mapped[str] = mapped_column(
        Enum(*content_types, name="content_type")
    )

    previous: Mapped[dict] = mapped_column(JSONB, nullable=True)
    changes: Mapped[dict] = mapped_column(JSONB)

    author_id = mapped_column(ForeignKey("service_users.id"))
    moderator_id = mapped_column(ForeignKey("service_users.id"))

    author: Mapped["User"] = relationship(
        back_populates="edits", foreign_keys=[author_id]
    )

    moderator: Mapped["User"] = relationship(
        back_populates="decisions", foreign_keys=[moderator_id]
    )
