from sqlalchemy.dialects.postgresql import JSONB
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

    client_id = mapped_column(
        ForeignKey("service_clients.id", ondelete="CASCADE"), nullable=True
    )
    client: Mapped["Client"] = relationship(back_populates="auth_tokens")

    # Scope required only for third-party clients
    # to allow access to requested data
    scope: Mapped[list[str]] = mapped_column(JSONB, server_default="[]")
