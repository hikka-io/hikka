from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from ..mixins import TitlesMixin
from datetime import datetime
from ..base import Base


class AnimeEpisode(Base, TitlesMixin):
    __tablename__ = "service_content_anime_episodes"

    type: Mapped[str] = mapped_column(String(32), nullable=True)
    aired: Mapped[datetime] = mapped_column(nullable=True)
    index: Mapped[int]

    anime_id = mapped_column(
        ForeignKey("service_content_anime.id"),
        index=True,
    )

    anime: Mapped["Anime"] = relationship(
        back_populates="episodes_list", foreign_keys=[anime_id]
    )
