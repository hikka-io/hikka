from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app import constants
from .base import Base


class Image(Base):
    __tablename__ = "service_images"

    path: Mapped[str] = mapped_column(unique=True)
    created: Mapped[datetime]

    @hybrid_property
    def url(self):
        return constants.CDN_ENDPOINT + self.path
