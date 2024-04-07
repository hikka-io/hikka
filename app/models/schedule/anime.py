from sqlalchemy.ext.hybrid import hybrid_property
from ..mixins import CreatedMixin, UpdatedMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from ..base import Base


class AnimeSchedule(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "service_schedule_anime"

    airing_at: Mapped[datetime]
    episode: Mapped[int]

    anime_id = mapped_column(ForeignKey("service_content_anime.id"), index=True)
    anime: Mapped["Anime"] = relationship(foreign_keys=[anime_id])

    @hybrid_property
    def time_left(self):
        now = datetime.now(UTC).replace(tzinfo=None)
        return self.airing_at - now
