from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from ..base import Base


class UserEditStats(Base):
    __tablename__ = "service_stats_edits"

    create: Mapped[int]
    update: Mapped[int]
    accept: Mapped[int]
    close: Mapped[int]
    deny: Mapped[int]

    user_id = mapped_column(ForeignKey("service_users.id"))

    user: Mapped["User"] = relationship(
        back_populates="following", foreign_keys=[user_id]
    )
