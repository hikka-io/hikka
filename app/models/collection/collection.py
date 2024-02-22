from sqlalchemy.dialects.postgresql import ARRAY
from ..mixins import CreatedMixin, UpdatedMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import String
from ..base import Base


class Collection(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "service_collections"

    labels: Mapped[list[str]] = mapped_column(ARRAY(String))
    description: Mapped[str] = mapped_column(nullable=True)
    title: Mapped[str] = mapped_column(String(255))

    content: Mapped[list["CollectionContent"]] = relationship(
        foreign_keys="[CollectionContent.collection_id]",
        back_populates="collection",
    )

    author_id = mapped_column(ForeignKey("service_users.id"))
    author: Mapped["User"] = relationship(
        back_populates="collections",
        foreign_keys=[author_id],
        lazy="selectin",
    )
