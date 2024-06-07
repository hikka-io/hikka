from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..mixins import CreatedMixin, UpdatedMixin, DeletedMixin
from sqlalchemy import String, ForeignKey
from ..base import Base
from uuid import UUID


class Read(Base, CreatedMixin, UpdatedMixin, DeletedMixin):
    __tablename__ = "service_read"
    __mapper_args__ = {
        "polymorphic_identity": "default",
        "polymorphic_on": "content_type",
        "with_polymorphic": "*",
    }

    note: Mapped[str] = mapped_column(nullable=True)
    chapters: Mapped[int] = mapped_column(default=0)
    volumes: Mapped[int] = mapped_column(default=0)
    rereads: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(16))
    score: Mapped[int] = mapped_column(default=0)

    content_type: Mapped[str]
    content_id: Mapped[UUID]

    user_id = mapped_column(ForeignKey("service_users.id"))

    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class MangaRead(Read):
    __mapper_args__ = {"polymorphic_identity": "manga"}

    content_id = mapped_column(
        ForeignKey("service_content_manga.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Manga"] = relationship(
        primaryjoin="Manga.id == MangaRead.content_id",
        foreign_keys=[content_id],
    )


class NovelRead(Read):
    __mapper_args__ = {"polymorphic_identity": "novel"}

    content_id = mapped_column(
        ForeignKey("service_content_novel.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Novel"] = relationship(
        primaryjoin="Novel.id == NovelRead.content_id",
        foreign_keys=[content_id],
    )
