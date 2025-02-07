from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from ..base import Base


class UserArticleStats(Base):
    __tablename__ = "service_stats_articles"

    # TODO: Moved to unified model (?)
    total: Mapped[int] = mapped_column(default=0)

    user_id = mapped_column(ForeignKey("service_users.id"))

    user: Mapped["User"] = relationship(foreign_keys=[user_id])
