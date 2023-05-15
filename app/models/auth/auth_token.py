from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from datetime import datetime
from ..base import Base


class AuthToken(Base):
    __tablename__ = "service_auth_tokens"

    secret: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expiration: Mapped[datetime]
    created: Mapped[datetime]

    user_id = mapped_column(ForeignKey("service_users.id"))

    user: Mapped["User"] = relationship(back_populates="auth_tokens")
