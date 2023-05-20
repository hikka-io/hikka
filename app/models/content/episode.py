from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from datetime import datetime
from ..base import Base


class AnimeEpisode(Base):
    __tablename__ = "service_content_anime_episodes"

    title_ja: Mapped[str] = mapped_column(nullable=True)
    title_en: Mapped[str] = mapped_column(nullable=True)
    title_ua: Mapped[str] = mapped_column(nullable=True)

    aired: Mapped[datetime] = mapped_column(nullable=True)
    index: Mapped[int]

    anime_id = mapped_column(ForeignKey("service_content_anime.id"))

    anime: Mapped["Anime"] = relationship(
        back_populates="episodes_list", foreign_keys=[anime_id]
    )
