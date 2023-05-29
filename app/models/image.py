from sqlalchemy.orm import Mapped
from datetime import datetime
from .base import Base


class Image(Base):
    __tablename__ = "service_images"

    created: Mapped[datetime]
    path: Mapped[str]
