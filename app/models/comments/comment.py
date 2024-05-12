from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import JSONB
from ..mixins import CreatedMixin, UpdatedMixin
from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import query_expression
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy_utils import LtreeType
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from ..base import Base
from uuid import UUID


class Comment(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "service_comments"
    __mapper_args__ = {
        "polymorphic_identity": "default",
        "polymorphic_on": "content_type",
    }

    # This field is used for comment visibility for private content
    private: Mapped[bool] = mapped_column(default=False)
    my_score: Mapped[int] = query_expression()

    history: Mapped[list] = mapped_column(JSONB, default=[])
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
    )

    @hybrid_property
    def slug(self):
        return str(self.reference)

    @hybrid_property
    def depth(self):
        return len(self.path)

    @hybrid_property
    def is_editable(self):
        now = datetime.now(UTC).replace(tzinfo=None)
        time_limit = timedelta(hours=1)
        max_edits = 5

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


class AnimeComment(Comment):
    __mapper_args__ = {"polymorphic_identity": "anime"}

    content_id = mapped_column(
        ForeignKey("service_content_anime.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Anime"] = relationship(
        primaryjoin="Anime.id == AnimeComment.content_id",
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
