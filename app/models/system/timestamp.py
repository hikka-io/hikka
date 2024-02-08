from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import String
from datetime import datetime
from ..base import Base


class SystemTimestamp(Base):
    __tablename__ = "service_system_timestamps"

    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    timestamp: Mapped[datetime]
