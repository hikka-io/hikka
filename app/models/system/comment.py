from ..mixins import CreatedMixin, UpdatedMixin
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

    path: Mapped[str] = mapped_column(LtreeType)
    content_type: Mapped[str]
    content_id: Mapped[UUID]
    text: Mapped[str]

    author_id = mapped_column(ForeignKey("service_users.id"))
    author: Mapped["User"] = relationship(
        back_populates="comments",
        foreign_keys=[author_id],
        lazy="selectin",
    )

    __table_args__ = (
        Index(
            "ix_comments_path",
            path,
            postgresql_using="gist",
        ),
    )


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
