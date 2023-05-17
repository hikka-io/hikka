from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import String
from datetime import datetime
from ..base import Base


class AnimeFranchise(Base):
    __tablename__ = "service_content_anime_franchises"

    # Multilang fields
    name_en: Mapped[str] = mapped_column(String(255), nullable=True)
    name_ua: Mapped[str] = mapped_column(String(255), nullable=True)

    updated: Mapped[datetime] = mapped_column(nullable=True)
    scored_by: Mapped[int] = mapped_column(default=0)
    score: Mapped[float] = mapped_column(default=0)

    anime: Mapped[list["Anime"]] = relationship(back_populates="franchise")
