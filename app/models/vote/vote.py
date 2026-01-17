from ..mixins import CreatedMixin, UpdatedMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from ..base import Base
from uuid import UUID


class Vote(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "service_votes"
    __mapper_args__ = {
        "polymorphic_identity": "default",
        "polymorphic_on": "content_type",
    }

    score: Mapped[int]  # Shoule be -1 / 0 / 1
    content_type: Mapped[str]
    content_id: Mapped[UUID]

    user_id = mapped_column(ForeignKey("service_users.id"), index=True)
    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class ArticleVote(Vote):
    __mapper_args__ = {"polymorphic_identity": "article"}

    content_id = mapped_column(
        ForeignKey("service_articles.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Article"] = relationship(
        primaryjoin="Article.id == ArticleVote.content_id",
        foreign_keys=[content_id],
    )


class CommentVote(Vote):
    __mapper_args__ = {"polymorphic_identity": "comment"}

    content_id = mapped_column(
        ForeignKey("service_comments.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Comment"] = relationship(
        primaryjoin="Comment.id == CommentVote.content_id",
        foreign_keys=[content_id],
    )


class CollectionVote(Vote):
    __mapper_args__ = {"polymorphic_identity": "collection"}

    content_id = mapped_column(
        ForeignKey("service_collections.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Collection"] = relationship(
        primaryjoin="Collection.id == CollectionVote.content_id",
        foreign_keys=[content_id],
    )
