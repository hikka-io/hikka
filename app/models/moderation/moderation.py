from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..mixins import CreatedMixin
from sqlalchemy import ForeignKey
from ..base import Base
from uuid import UUID


class Moderation(Base, CreatedMixin):
    __tablename__ = "service_moderation"
    __mapper_args__ = {
        "polymorphic_identity": "default",
        "polymorphic_on": "content_type",
    }

    content_type: Mapped[str]
    content_id: Mapped[UUID]

    user_id = mapped_column(ForeignKey("service_users.id"))
    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class EditModeration(Moderation):
    __mapper_args__ = {
        "polymorphic_identity": "edit",
        "eager_defaults": True,
    }

    content_id = mapped_column(
        ForeignKey("service_edits.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Edit"] = relationship(
        primaryjoin="Edit.id == EditModeration.content_id",
        foreign_keys=[content_id],
        lazy="immediate",
    )
