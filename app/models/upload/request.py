from ..mixins import CreatedMixin, UpdatedMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import String
from datetime import datetime
from ..base import Base


class UploadRequest(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "service_upload_requests"

    secret: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    type: Mapped[str] = mapped_column(String(32))
    expiration: Mapped[datetime]
    mime_type: Mapped[str]
    path: Mapped[str]
    size: Mapped[int]

    user_id = mapped_column(ForeignKey("service_users.id"))

    image_id = mapped_column(
        ForeignKey("service_images.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    image_relation: Mapped["Image"] = relationship()
