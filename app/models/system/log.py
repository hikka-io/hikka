from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import String
from datetime import datetime
from ..base import Base
from uuid import UUID


class Log(Base):
    __tablename__ = "service_logs"

    log_type: Mapped[str] = mapped_column(String(64), index=True)
    target_id: Mapped[UUID] = mapped_column(nullable=True)
    created: Mapped[datetime] = mapped_column(index=True)
    data: Mapped[dict] = mapped_column(JSONB, default={})

    user_id = mapped_column(ForeignKey("service_users.id"))
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
