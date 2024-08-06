from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

from ..base import Base


class Client(Base):
    __tablename__ = "service_clients"

    secret: Mapped[str] = mapped_column(String(128))

    name: Mapped[str]
    description: Mapped[str]
    endpoint: Mapped[str]
    verified: Mapped[bool] = mapped_column(default=False)

    user_id = mapped_column(ForeignKey("service_users.id"))
    user: Mapped["User"] = relationship(foreign_keys=user_id)

    auth_tokens: Mapped[list["AuthToken"]] = relationship(
        back_populates="client",
    )

    created: Mapped[datetime]
    updated: Mapped[datetime]
