from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from ..mixins import CreatedMixin
from datetime import datetime
from ..base import Base


class AnimeSchedule(Base, CreatedMixin):
    __tablename__ = "service_schedule_anime"

    airing_at: Mapped[datetime]
    episode: Mapped[int]

    anime_id = mapped_column(
        ForeignKey("service_content_anime.id"),
        index=True,
    )

    anime: Mapped["Anime"] = relationship(
        back_populates="characters", foreign_keys=[anime_id]
    )
