from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from datetime import datetime
from ..base import Base


class Follow(Base):
    __tablename__ = "service_follows"

    created: Mapped[datetime]

    followed_user_id = mapped_column(ForeignKey("service_users.id"))
    user_id = mapped_column(ForeignKey("service_users.id"))

    followed_user: Mapped["User"] = relationship(back_populates="followers")
    user: Mapped["User"] = relationship(back_populates="following")
