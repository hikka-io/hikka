from ..mixins import CreatedMixin, UpdatedMixin
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import String
from ..base import Base
from uuid import UUID


class Activity(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "service_activity"
    __mapper_args__ = {
        "polymorphic_identity": "default",
        "polymorphic_on": "activity_type",
    }

    activity_type: Mapped[str] = mapped_column(String(64), index=True)
    target_id: Mapped[UUID] = mapped_column(nullable=True)
    data: Mapped[dict] = mapped_column(JSONB, default={})

    user_id = mapped_column(ForeignKey("service_users.id"))
    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class FavouriteActivity(Activity):
    __mapper_args__ = {
        "polymorphic_identity": "favourite",
        "eager_defaults": True,
    }

    target_id = mapped_column(
        ForeignKey("service_content_anime.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    target: Mapped["Anime"] = relationship(
        primaryjoin="Anime.id == FavouriteActivity.target_id",
        foreign_keys=[target_id],
        # lazy="immediate",  # ToDo: check if it is good idea
    )


# class SignupActivity(Activity):
#     __mapper_args__ = {
#         "polymorphic_identity": "signup",
#         "eager_defaults": True,
#     }
