from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import ARRAY
from ..mixins import CreatedMixin, UpdatedMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import String
from ..base import Base
from uuid import UUID


class History(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "service_user_history"
    # __mapper_args__ = {
    #     "polymorphic_identity": "default",
    #     "polymorphic_on": "history_type",
    # }

    history_type: Mapped[str] = mapped_column(String(64), index=True)
    target_id: Mapped[UUID] = mapped_column(nullable=True)
    data: Mapped[dict] = mapped_column(JSONB, default={})

    user_id = mapped_column(ForeignKey("service_users.id"))
    user: Mapped["User"] = relationship(foreign_keys=[user_id])

    used_logs: Mapped[list[str]] = mapped_column(ARRAY(String))


# class FavouriteHistory(Edit):
#     __mapper_args__ = {
#         "polymorphic_identity": "watch",
#         "eager_defaults": True,
#     }

#     content_id = mapped_column(
#         ForeignKey("service_content_anime.id", ondelete="CASCADE"),
#         use_existing_column=True,
#         index=True,
#     )

#     content: Mapped["Anime"] = relationship(
#         primaryjoin="Anime.id == AnimeEdit.content_id",
#         foreign_keys=[content_id],
#         lazy="immediate",  # ToDo: check if it is good idea
#     )
