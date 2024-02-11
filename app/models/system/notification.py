from sqlalchemy.dialects.postgresql import JSONB
from ..mixins import CreatedMixin, UpdatedMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import String
from app import constants
from ..base import Base
from uuid import UUID


class Notification(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "service_notifications"
    __mapper_args__ = {
        "polymorphic_identity": "default",
        "polymorphic_on": "notification_type",
    }

    notification_type: Mapped[str] = mapped_column(String(64), index=True)
    target_id: Mapped[UUID] = mapped_column(nullable=True)
    data: Mapped[dict] = mapped_column(JSONB, default={})
    log_id: Mapped[UUID] = mapped_column(nullable=True)
    seen: Mapped[bool] = mapped_column(default=False)

    user_id = mapped_column(ForeignKey("service_users.id"))
    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class EditCommentNotification(Notification):
    __mapper_args__ = {
        "polymorphic_identity": constants.NOTIFICATION_EDIT_COMMENT,
        "eager_defaults": True,
    }

    target_id = mapped_column(
        ForeignKey("service_comments.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Comment"] = relationship(
        primaryjoin="Comment.id == EditCommentNotification.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # ToDo: check if it is good idea
    )


class CommentReplyNotification(Notification):
    __mapper_args__ = {
        "polymorphic_identity": constants.NOTIFICATION_COMMENT_REPLY,
        "eager_defaults": True,
    }

    target_id = mapped_column(
        ForeignKey("service_comments.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Comment"] = relationship(
        primaryjoin="Comment.id == CommentReplyNotification.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # ToDo: check if it is good idea
    )


class CommentTagNotification(Notification):
    __mapper_args__ = {
        "polymorphic_identity": constants.NOTIFICATION_COMMENT_TAG,
        "eager_defaults": True,
    }

    target_id = mapped_column(
        ForeignKey("service_comments.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Comment"] = relationship(
        primaryjoin="Comment.id == CommentTagNotification.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # ToDo: check if it is good idea
    )


class EditAcceptedNotification(Notification):
    __mapper_args__ = {
        "polymorphic_identity": constants.NOTIFICATION_EDIT_ACCEPTED,
        "eager_defaults": True,
    }

    target_id = mapped_column(
        ForeignKey("service_edits.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Edit"] = relationship(
        primaryjoin="Edit.id == EditAcceptedNotification.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # ToDo: check if it is good idea
    )


class EditDeniedNotification(Notification):
    __mapper_args__ = {
        "polymorphic_identity": constants.NOTIFICATION_EDIT_DENIED,
        "eager_defaults": True,
    }

    target_id = mapped_column(
        ForeignKey("service_edits.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Edit"] = relationship(
        primaryjoin="Edit.id == EditDeniedNotification.target_id",
        foreign_keys=[target_id],
        lazy="immediate",  # ToDo: check if it is good idea
    )
