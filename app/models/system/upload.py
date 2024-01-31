from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from ..mixins import CreatedMixin
from sqlalchemy import String
from ..base import Base


class Upload(Base, CreatedMixin):
    __tablename__ = "service_uploads"

    type: Mapped[str] = mapped_column(String(32))
    mime_type: Mapped[str]
    path: Mapped[str]
    size: Mapped[int]

    user_id = mapped_column(ForeignKey("service_users.id"))
    user: Mapped["User"] = relationship(foreign_keys=[user_id])

    image_id = mapped_column(
        ForeignKey("service_images.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    image: Mapped["Image"] = relationship(lazy="selectin")
