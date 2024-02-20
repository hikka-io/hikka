from ..mixins import CreatedMixin, UpdatedMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import String
from ..base import Base


class CollectionGroup(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "service_collection_groups"

    title: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str]
    order: Mapped[int]

    collection_id = mapped_column(ForeignKey("service_collections.id"))
    collection: Mapped["Collection"] = relationship(
        back_populates="groups", foreign_keys=[collection_id]
    )
