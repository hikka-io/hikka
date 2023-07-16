from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column
from .mixins import CreatedMixin
from app import constants
from .base import Base


class Image(Base, CreatedMixin):
    __tablename__ = "service_images"

    uploaded: Mapped[bool] = mapped_column(default=False)
    ignore: Mapped[bool] = mapped_column(default=False)
    path: Mapped[str] = mapped_column(unique=True)

    @hybrid_property
    def url(self):
        return constants.CDN_ENDPOINT + self.path
