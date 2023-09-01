from sqlalchemy import Enum, ForeignKey, String, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from app import constants
from ..base import Base
from uuid import UUID

from ..mixins import (
    CreatedMixin,
    UpdatedMixin,
)


statuses = (
    constants.EDIT_PENDING,
    constants.EDIT_APPROVED,
    constants.EDIT_DENIED,
    constants.EDIT_CLOSED,
)

content_types = (
    constants.CONTENT_ANIME,
    constants.CONTENT_MANGA,
    constants.CONTENT_CHARACTER,
    constants.CONTENT_COMPANY,
    constants.CONTENT_EPISODE,
    constants.CONTENT_GENRE,
    constants.CONTENT_PERSON,
    constants.CONTENT_STAFF,
)


class ContentEdit(
    Base,
    CreatedMixin,
    UpdatedMixin,
):
    __tablename__ = "service_edits"

    edit_id: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, primary_key=True, autoincrement=True
    )
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
