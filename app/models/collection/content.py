from ..mixins import CreatedMixin, UpdatedMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import String
from ..base import Base
from uuid import UUID


class CollectionGroupContent(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "service_collection_group_content"
    __mapper_args__ = {
        "polymorphic_identity": "default",
        "polymorphic_on": "content_type",
    }

    comment: Mapped[str] = mapped_column(nullable=True)
    content_type: Mapped[str]
    content_id: Mapped[UUID]
    order: Mapped[int]


class AnimeCollectionGroupContent(CollectionGroupContent):
    __mapper_args__ = {
        "polymorphic_identity": "anime",
        # "eager_defaults": True,
    }

    content_id = mapped_column(
        ForeignKey("service_content_anime.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Anime"] = relationship(
        primaryjoin="Anime.id == AnimeCollectionGroupContent.content_id",
        foreign_keys=[content_id],
        # lazy="immediate",  # ToDo: check if it is good idea
    )
