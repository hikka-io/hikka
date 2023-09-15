from sqlalchemy.dialects.postgresql import JSONB
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


class ContentEdit(
    Base,
    CreatedMixin,
    UpdatedMixin,
):
    __tablename__ = "service_edits"

    description: Mapped[str] = mapped_column(nullable=True)
    hidden: Mapped[bool] = mapped_column(default=False)
    content_type: Mapped[str]
    content_id: Mapped[UUID]
    status: Mapped[str]

    edit_id: Mapped[int] = mapped_column(
        unique=True, index=True, autoincrement=True, primary_key=True
    )

    before: Mapped[dict] = mapped_column(JSONB, nullable=True)
    after: Mapped[dict] = mapped_column(JSONB)

    moderator_id = mapped_column(ForeignKey("service_users.id"))
    author_id = mapped_column(ForeignKey("service_users.id"))

    moderator: Mapped["User"] = relationship(
        back_populates="decisions", foreign_keys=[moderator_id]
    )

    author: Mapped["User"] = relationship(
        back_populates="edits", foreign_keys=[author_id]
    )
