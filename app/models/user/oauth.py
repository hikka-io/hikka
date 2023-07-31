from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy import String
from datetime import datetime
from ..base import Base


class UserOAuth(Base):
    __tablename__ = "service_user_oauth"

    provider: Mapped[str] = mapped_column(String(255))
    oauth_id = mapped_column(String(32))

    last_used: Mapped[datetime]
    created: Mapped[datetime]

    user_id = mapped_column(ForeignKey("service_users.id"))

    user: Mapped["User"] = relationship(
        back_populates="oauth_providers", foreign_keys=[user_id]
    )
