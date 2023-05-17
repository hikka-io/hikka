from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import String


class ContentMixin:
    content_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
