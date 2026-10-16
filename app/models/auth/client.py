from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from ..mixins import DeletedMixin
from datetime import datetime
from ..base import Base


class Client(Base, DeletedMixin):
    __tablename__ = "service_clients"

    secret: Mapped[str] = mapped_column(String(128))

    verified: Mapped[bool] = mapped_column(default=False)
    created: Mapped[datetime]
    updated: Mapped[datetime]
    description: Mapped[str]
    endpoint: Mapped[str]
    name: Mapped[str]

    user_id = mapped_column(ForeignKey("service_users.id"))
    user: Mapped["User"] = relationship(foreign_keys=user_id)

    auth_tokens: Mapped[list["AuthToken"]] = relationship(
        back_populates="client",
    )
