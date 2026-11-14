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
        "with_polymorphic": "*",
    }

    history_type: Mapped[str] = mapped_column(String(64), index=True)
    target_id: Mapped[UUID] = mapped_column(nullable=True)
    data: Mapped[dict] = mapped_column(JSONB, default={})

    user_id = mapped_column(ForeignKey("service_users.id"), index=True)
    user: Mapped["User"] = relationship(foreign_keys=[user_id])

    used_logs: Mapped[list[str]] = mapped_column(ARRAY(String))


class FavouriteAnimeHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_FAVOURITE_ANIME,
        "eager_defaults": True,
    }

    content: Mapped["Anime"] = relationship(
        primaryjoin="Anime.id == FavouriteAnimeHistory.target_id",
        foreign_keys="FavouriteAnimeHistory.target_id",
        lazy="selectin",
    )


class FavouriteAnimeRemoveHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_FAVOURITE_ANIME_REMOVE,
        "eager_defaults": True,
    }

    content: Mapped["Anime"] = relationship(
        primaryjoin="Anime.id == FavouriteAnimeRemoveHistory.target_id",
        foreign_keys="FavouriteAnimeRemoveHistory.target_id",
        lazy="selectin",
    )


class FavouriteMangaHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_FAVOURITE_MANGA,
        "eager_defaults": True,
    }

    content: Mapped["Manga"] = relationship(
        primaryjoin="Manga.id == FavouriteMangaHistory.target_id",
        foreign_keys="FavouriteMangaHistory.target_id",
        lazy="selectin",
    )


class FavouriteMangaRemoveHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_FAVOURITE_MANGA_REMOVE,
        "eager_defaults": True,
    }

    content: Mapped["Manga"] = relationship(
        primaryjoin="Manga.id == FavouriteMangaRemoveHistory.target_id",
        foreign_keys="FavouriteMangaRemoveHistory.target_id",
        lazy="selectin",
    )


class FavouriteNovelHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_FAVOURITE_NOVEL,
        "eager_defaults": True,
    }

    content: Mapped["Novel"] = relationship(
        primaryjoin="Novel.id == FavouriteNovelHistory.target_id",
        foreign_keys="FavouriteNovelHistory.target_id",
        lazy="selectin",
    )


class FavouriteNovelRemoveHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_FAVOURITE_NOVEL_REMOVE,
        "eager_defaults": True,
    }

    content: Mapped["Novel"] = relationship(
        primaryjoin="Novel.id == FavouriteNovelRemoveHistory.target_id",
        foreign_keys="FavouriteNovelRemoveHistory.target_id",
        lazy="selectin",
    )


class WatchHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_WATCH,
        "eager_defaults": True,
    }

    content: Mapped["Anime"] = relationship(
        primaryjoin="Anime.id == WatchHistory.target_id",
        foreign_keys="WatchHistory.target_id",
        lazy="selectin",
    )


class WatchDeleteHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_WATCH_DELETE,
        "eager_defaults": True,
    }

    content: Mapped["Anime"] = relationship(
        primaryjoin="Anime.id == WatchDeleteHistory.target_id",
        foreign_keys="WatchDeleteHistory.target_id",
        lazy="selectin",
    )


class WatchImportHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_WATCH_IMPORT,
        "eager_defaults": True,
    }


class ReadImportHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_READ_IMPORT,
        "eager_defaults": True,
    }


class ReadMangaHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_READ_MANGA,
        "eager_defaults": True,
    }

    content: Mapped["Manga"] = relationship(
        primaryjoin="Manga.id == ReadMangaHistory.target_id",
        foreign_keys="ReadMangaHistory.target_id",
        lazy="selectin",
    )


class ReadMangaDeleteHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_READ_MANGA_DELETE,
        "eager_defaults": True,
    }

    content: Mapped["Manga"] = relationship(
        primaryjoin="Manga.id == ReadMangaDeleteHistory.target_id",
        foreign_keys="ReadMangaDeleteHistory.target_id",
        lazy="selectin",
    )


class ReadNovelHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_READ_NOVEL,
        "eager_defaults": True,
    }

    content: Mapped["Novel"] = relationship(
        primaryjoin="Novel.id == ReadNovelHistory.target_id",
        foreign_keys="ReadNovelHistory.target_id",
        lazy="selectin",
    )


class ReadNovelDeleteHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_READ_NOVEL_DELETE,
        "eager_defaults": True,
    }

    content: Mapped["Novel"] = relationship(
        primaryjoin="Novel.id == ReadNovelDeleteHistory.target_id",
        foreign_keys="ReadNovelDeleteHistory.target_id",
        lazy="selectin",
    )
