from sqlalchemy.dialects.postgresql import JSONB
from ..mixins import CreatedMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import String
from ..base import Base
from uuid import UUID


class Moderation(Base, CreatedMixin):
    __tablename__ = "service_moderation"

    target_type: Mapped[str] = mapped_column(String(64), index=True)
    data: Mapped[dict] = mapped_column(JSONB, default={})
    log_id: Mapped[UUID] = mapped_column(nullable=True)

    user_id = mapped_column(ForeignKey("service_users.id"))
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
