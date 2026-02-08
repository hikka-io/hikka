from sqlalchemy.dialects.postgresql import JSONB
from ..mixins import CreatedMixin, UpdatedMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from ..base import Base


class Digest(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "service_artifacts"

    data: Mapped[dict] = mapped_column(JSONB, default={})
    private: Mapped[bool] = mapped_column(default=True)
    name: Mapped[str] = mapped_column(index=True)

    user_id = mapped_column(ForeignKey("service_users.id"))
    user: Mapped["User"] = relationship(foreign_keys=[user_id])

    __table_args__ = (
        Index("idx_user_artifact_lookup", "user_id", "name", unique=True),
    )
