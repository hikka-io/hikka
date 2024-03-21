from ..mixins import CreatedMixin, UpdatedMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from ..base import Base


class CommentVoteLegacy(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "service_comment_votes"

    score: Mapped[int]  # Shoule be -1 / 0 / 1

    user_id = mapped_column(ForeignKey("service_users.id"))
    user: Mapped["User"] = relationship(foreign_keys=[user_id])

    comment_id = mapped_column(ForeignKey("service_comments.id"))
    comment: Mapped["Comment"] = relationship(foreign_keys=[comment_id])
