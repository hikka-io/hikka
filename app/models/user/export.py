from sqlalchemy.dialects.postgresql import JSONB
from ..mixins import CreatedMixin, UpdatedMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from ..base import Base


class UserExport(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "service_user_exports"

    anime: Mapped[list] = mapped_column(JSONB, default=[])
    manga: Mapped[list] = mapped_column(JSONB, default=[])
    novel: Mapped[list] = mapped_column(JSONB, default=[])

    user_id = mapped_column(ForeignKey("service_users.id"))

    user: Mapped["User"] = relationship(foreign_keys=[user_id])
