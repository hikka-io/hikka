from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, UniqueConstraint
from datetime import datetime
from ..base import Base


class AnimeWatch(Base):
    __tablename__ = "service_watch"

    # Watch fields
    rewatches: Mapped[int] = mapped_column(default=0)
    note: Mapped[str] = mapped_column(nullable=True)
    episodes: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(16))
    score: Mapped[int] = mapped_column(default=0)

    # System fields
    duration: Mapped[int] = mapped_column(default=0)
    created: Mapped[datetime]
    updated: Mapped[datetime]

    anime_id = mapped_column(ForeignKey("service_content_anime.id"))
    user_id = mapped_column(ForeignKey("service_users.id"))

    anime: Mapped["Anime"] = relationship(
        back_populates="watch", foreign_keys=[anime_id]
    )

    user: Mapped["User"] = relationship(
        back_populates="watch", foreign_keys=[user_id]
    )

    unique_constraint = UniqueConstraint(anime_id, user_id)
