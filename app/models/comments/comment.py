from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy_utils import LtreeType
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import text
from ..base import Base
from uuid import UUID

from ..mixins import (
    MyScoreMixin,
    CreatedMixin,
    UpdatedMixin,
    DeletedMixin,
)


class Comment(
    MyScoreMixin,
    CreatedMixin,
    UpdatedMixin,
    DeletedMixin,
    Base,
):
    __tablename__ = "service_comments"
    __mapper_args__ = {
        "polymorphic_identity": "default",
        "polymorphic_on": "content_type",
    }

    # This field is used for comment visibility for private content
    private: Mapped[bool] = mapped_column(default=False)

    history: Mapped[list] = mapped_column(JSONB, default=[])
    preview: Mapped[dict] = mapped_column(JSONB, default={})
    hidden: Mapped[bool] = mapped_column(default=False)
    score: Mapped[int] = mapped_column(nullable=False)
    path: Mapped[str] = mapped_column(LtreeType)
    content_type: Mapped[str]
    content_id: Mapped[UUID]
    vote_score: Mapped[int]
    text: Mapped[str]

    hidden_by_id = mapped_column(ForeignKey("service_users.id"))
    hidden_by: Mapped["User"] = relationship(
        foreign_keys=[hidden_by_id],
    )

    author_id = mapped_column(ForeignKey("service_users.id"))
    author: Mapped["User"] = relationship(
        foreign_keys=[author_id], lazy="selectin"
    )

    __table_args__ = (
        Index(
            "ix_comments_path",
            path,
            postgresql_using="gist",
        ),
        Index(
            "ix_comment_latest",
            text("created DESC"),
            postgresql_where=text(
                "nlevel(path) = 1 AND NOT hidden AND NOT private AND NOT deleted"
            ),
        ),
    )

    @hybrid_property
    def slug(self):
        return str(self.reference)

    @hybrid_property
    def depth(self):
        return len(self.path)

    @hybrid_property
    def is_editable(self):
        # TODO: this is bad place for such limits
        # We shold move them somewhere more sensible
        now = datetime.now(UTC).replace(tzinfo=None)
        time_limit = timedelta(hours=24)
        max_edits = 500

        if len(self.history) >= max_edits:
            return False

        if now > self.created + time_limit:
            return False

        return True


class EditComment(Comment):
    __mapper_args__ = {"polymorphic_identity": "edit"}

    content_id = mapped_column(
        ForeignKey("service_edits.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Edit"] = relationship(
        primaryjoin="Edit.id == EditComment.content_id",
        foreign_keys=[content_id],
    )


class CollectionComment(Comment):
    __mapper_args__ = {"polymorphic_identity": "collection"}

    content_id = mapped_column(
        ForeignKey("service_collections.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Collection"] = relationship(
        primaryjoin="Collection.id == CollectionComment.content_id",
        foreign_keys=[content_id],
    )


class AnimeComment(Comment):
    __mapper_args__ = {
        "polymorphic_identity": "anime",
    }

    content_id = mapped_column(
        ForeignKey("service_content_anime.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Anime"] = relationship(
        primaryjoin="Anime.id == AnimeComment.content_id",
        foreign_keys=[content_id],
    )


class MangaComment(Comment):
    __mapper_args__ = {
        "polymorphic_identity": "manga",
    }

    content_id = mapped_column(
        ForeignKey("service_content_manga.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Manga"] = relationship(
        primaryjoin="Manga.id == MangaComment.content_id",
        foreign_keys=[content_id],
    )


class NovelComment(Comment):
    __mapper_args__ = {
        "polymorphic_identity": "novel",
    }

    content_id = mapped_column(
        ForeignKey("service_content_novel.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Novel"] = relationship(
        primaryjoin="Novel.id == NovelComment.content_id",
        foreign_keys=[content_id],
    )


class ArticleComment(Comment):
    __mapper_args__ = {
        "polymorphic_identity": "article",
    }

    content_id = mapped_column(
        ForeignKey("service_articles.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Article"] = relationship(
        primaryjoin="Article.id == ArticleComment.content_id",
        foreign_keys=[content_id],
    )
