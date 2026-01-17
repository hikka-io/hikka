from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship
from ..mixins import CreatedMixin
from datetime import datetime
from app import constants
from ..base import Base
from uuid import UUID


class Image(Base, CreatedMixin):
    __tablename__ = "service_images"

    deletion_request: Mapped[bool] = mapped_column(default=False)
    path: Mapped[str] = mapped_column(unique=True, index=True)
    deleted: Mapped[datetime] = mapped_column(nullable=True)
    uploaded: Mapped[bool] = mapped_column(default=False)
    ignore: Mapped[bool] = mapped_column(default=False)
    used: Mapped[bool] = mapped_column(default=True)

    height: Mapped[int] = mapped_column(default=None, nullable=True)
    width: Mapped[int] = mapped_column(default=None, nullable=True)

    type: Mapped[str] = mapped_column(String(32), nullable=True)
    mime_type: Mapped[str] = mapped_column(nullable=True)
    system: Mapped[bool] = mapped_column(default=False)
    size: Mapped[int] = mapped_column(nullable=True)

    user_id = mapped_column(ForeignKey("service_users.id", use_alter=True))
    user: Mapped["User"] = relationship(foreign_keys=[user_id])

    attachment_content_type: Mapped[str] = mapped_column(
        nullable=True, index=True
    )

    attachment_content_id: Mapped[UUID] = mapped_column(
        nullable=True, index=True
    )

    @hybrid_property
    def url(self):
        return constants.CDN_ENDPOINT + self.path
