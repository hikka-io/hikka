from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import ForeignKey

from ..base import Base


class AuthTokenRequest(Base):
    __tablename__ = "service_auth_token_requests"

    expiration: Mapped[datetime]
    created: Mapped[datetime]

    user_id = mapped_column(ForeignKey("service_users.id"))

    user: Mapped["User"] = relationship()

    client_id = mapped_column(
        ForeignKey("service_clients.id", ondelete="CASCADE")
    )
    client: Mapped["Client"] = relationship()

    scope: Mapped[list[str]] = mapped_column(JSONB)
