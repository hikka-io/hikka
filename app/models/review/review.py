from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import String
from ..base import Base
from uuid import UUID

from ..mixins import (
    CreatedMixin,
    UpdatedMixin,
)


class Review(
    Base,
    CreatedMixin,
    UpdatedMixin,
):
    __tablename__ = "service_reviews"
    __mapper_args__ = {
        "polymorphic_identity": "default",
        "polymorphic_on": "content_type",
        "with_polymorphic": "*",
    }

    recommended: Mapped[str] = mapped_column(String(16), index=True)

    content_type: Mapped[str]
    content_id: Mapped[UUID]

    comment_id = mapped_column(
        ForeignKey("service_comments.id", ondelete="CASCADE")
    )

    comment: Mapped["Comment"] = relationship(
        foreign_keys=[comment_id], back_populates="review"
    )

    user_id = mapped_column(ForeignKey("service_users.id"), index=True)

    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class AnimeReview(Review):
    __mapper_args__ = {"polymorphic_identity": "anime"}

    content_id = mapped_column(
        ForeignKey("service_content_anime.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Anime"] = relationship(
        primaryjoin="Anime.id == AnimeReview.content_id",
        foreign_keys=[content_id],
    )


class MangaReview(Review):
    __mapper_args__ = {"polymorphic_identity": "manga"}

    content_id = mapped_column(
        ForeignKey("service_content_manga.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Manga"] = relationship(
        primaryjoin="Manga.id == MangaReview.content_id",
        foreign_keys=[content_id],
    )


class NovelReview(Review):
    __mapper_args__ = {"polymorphic_identity": "novel"}

    content_id = mapped_column(
        ForeignKey("service_content_novel.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Novel"] = relationship(
        primaryjoin="Novel.id == NovelReview.content_id",
        foreign_keys=[content_id],
    )
