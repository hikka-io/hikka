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


class FavouriteAnimeHistory(History):
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
        primaryjoin="Anime.id == FavouriteAnimeHistory.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # TODO: check if it is good idea
    )


class FavouriteAnimeRemoveHistory(History):
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
        primaryjoin="Anime.id == FavouriteAnimeRemoveHistory.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # TODO: check if it is good idea
    )


class FavouriteMangaHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_FAVOURITE_MANGA,
        "eager_defaults": True,
    }

    target_id = mapped_column(
        ForeignKey("service_content_manga.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Manga"] = relationship(
        primaryjoin="Manga.id == FavouriteMangaHistory.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # TODO: check if it is good idea
    )


class FavouriteMangaRemoveHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_FAVOURITE_MANGA_REMOVE,
        "eager_defaults": True,
    }

    target_id = mapped_column(
        ForeignKey("service_content_manga.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Manga"] = relationship(
        primaryjoin="Manga.id == FavouriteMangaRemoveHistory.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # TODO: check if it is good idea
    )


class FavouriteNovelHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_FAVOURITE_NOVEL,
        "eager_defaults": True,
    }

    target_id = mapped_column(
        ForeignKey("service_content_novel.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Novel"] = relationship(
        primaryjoin="Novel.id == FavouriteNovelHistory.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # TODO: check if it is good idea
    )


class FavouriteNovelRemoveHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_FAVOURITE_NOVEL_REMOVE,
        "eager_defaults": True,
    }

    target_id = mapped_column(
        ForeignKey("service_content_novel.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Novel"] = relationship(
        primaryjoin="Novel.id == FavouriteNovelRemoveHistory.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # TODO: check if it is good idea
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
        lazy="immediate",  # TODO: check if it is good idea
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
        lazy="immediate",  # TODO: check if it is good idea
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

    target_id = mapped_column(
        ForeignKey("service_content_manga.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Manga"] = relationship(
        primaryjoin="Manga.id == ReadMangaHistory.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # TODO: check if it is good idea
    )


class ReadMangaDeleteHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_READ_MANGA_DELETE,
        "eager_defaults": True,
    }

    target_id = mapped_column(
        ForeignKey("service_content_manga.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Manga"] = relationship(
        primaryjoin="Manga.id == ReadMangaDeleteHistory.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # TODO: check if it is good idea
    )


class ReadNovelHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_READ_NOVEL,
        "eager_defaults": True,
    }

    target_id = mapped_column(
        ForeignKey("service_content_novel.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Novel"] = relationship(
        primaryjoin="Novel.id == ReadNovelHistory.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # TODO: check if it is good idea
    )


class ReadNovelDeleteHistory(History):
    __mapper_args__ = {
        "polymorphic_identity": constants.HISTORY_READ_NOVEL_DELETE,
        "eager_defaults": True,
    }

    target_id = mapped_column(
        ForeignKey("service_content_novel.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Novel"] = relationship(
        primaryjoin="Novel.id == ReadNovelDeleteHistory.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # TODO: check if it is good idea
    )
