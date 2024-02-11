from sqlalchemy.dialects.postgresql import JSONB
from ..mixins import CreatedMixin, UpdatedMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import String
from ..base import Base
from uuid import UUID


class Notification(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "service_notifications"

    notification_type: Mapped[str] = mapped_column(String(64), index=True)
    data: Mapped[dict] = mapped_column(JSONB, default={})
    log_id: Mapped[UUID] = mapped_column(nullable=True)
    seen: Mapped[bool] = mapped_column(default=False)

    user_id = mapped_column(ForeignKey("service_users.id"))
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
