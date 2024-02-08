from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import ARRAY
from ..mixins import CreatedMixin, UpdatedMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import String
from app import constants
from ..base import Base
from uuid import UUID


class History(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "service_user_history"
    __mapper_args__ = {
        "polymorphic_identity": "default",
        "polymorphic_on": "history_type",
    }

    history_type: Mapped[str] = mapped_column(String(64), index=True)
    target_id: Mapped[UUID] = mapped_column(nullable=True)
    data: Mapped[dict] = mapped_column(JSONB, default={})

    user_id = mapped_column(ForeignKey("service_users.id"))
    user: Mapped["User"] = relationship(foreign_keys=[user_id])

    used_logs: Mapped[list[str]] = mapped_column(ARRAY(String))


class FavouriteHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_FAVOURITE_ANIME,
        "eager_defaults": True,
    }

    target_id = mapped_column(
        ForeignKey("service_content_anime.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Anime"] = relationship(
        primaryjoin="Anime.id == FavouriteHistory.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # ToDo: check if it is good idea
    )


class FavouriteRemoveHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_FAVOURITE_ANIME_REMOVE,
        "eager_defaults": True,
    }

    target_id = mapped_column(
        ForeignKey("service_content_anime.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Anime"] = relationship(
        primaryjoin="Anime.id == FavouriteRemoveHistory.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # ToDo: check if it is good idea
    )


class WatchHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_WATCH,
        "eager_defaults": True,
    }

    target_id = mapped_column(
        ForeignKey("service_content_anime.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Anime"] = relationship(
        primaryjoin="Anime.id == WatchHistory.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # ToDo: check if it is good idea
    )


class WatchDeleteHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_WATCH_DELETE,
        "eager_defaults": True,
    }

    target_id = mapped_column(
        ForeignKey("service_content_anime.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Anime"] = relationship(
        primaryjoin="Anime.id == WatchDeleteHistory.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # ToDo: check if it is good idea
    )
