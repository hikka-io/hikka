from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from datetime import datetime
from ..base import Base


class AnimeFavourite(Base):
    __tablename__ = "service_favourite_anime"

    created: Mapped[datetime]

    anime_id = mapped_column(ForeignKey("service_content_anime.id"))
    user_id = mapped_column(ForeignKey("service_users.id"))

    anime: Mapped["Anime"] = relationship(
        back_populates="favourite", foreign_keys=[anime_id]
    )

    user: Mapped["User"] = relationship(
        back_populates="favourite", foreign_keys=[user_id]
    )

    unique_constraint = UniqueConstraint(anime_id, user_id)
