from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from datetime import datetime
from ..base import Base


class EmailMessage(Base):
    __tablename__ = "service_email_messages"

    sent_time: Mapped[datetime] = mapped_column(default=None, nullable=True)
    sent: Mapped[bool] = mapped_column(default=False)
    type: Mapped[str] = mapped_column(String(32))
    created: Mapped[datetime]
    content: Mapped[str]

    user_id = mapped_column(ForeignKey("service_users.id"))

    user: Mapped["User"] = relationship(back_populates="email_messages")
