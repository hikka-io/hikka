from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import String
from datetime import datetime
from ..base import Base


class Activity(Base):
    __tablename__ = "service_user_activity"

    period: Mapped[str] = mapped_column(String(64), index=True)
    used_logs: Mapped[list[str]] = mapped_column(ARRAY(String))
    timestamp: Mapped[datetime] = mapped_column(index=True)
    actions: Mapped[int]

    user_id = mapped_column(ForeignKey("service_users.id"))
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
