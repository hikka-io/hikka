from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from ..base import Base
from uuid import UUID


class CollectionContent(Base):
    __tablename__ = "service_collection_content"
    __mapper_args__ = {
        "polymorphic_identity": "default",
        "polymorphic_on": "content_type",
    }

    comment: Mapped[str] = mapped_column(nullable=True)
    label: Mapped[str] = mapped_column(nullable=True)
    content_type: Mapped[str]
    content_id: Mapped[UUID]
    order: Mapped[int]

    collection_id = mapped_column(ForeignKey("service_collections.id"))
    collection: Mapped["Collection"] = relationship(
        foreign_keys=[collection_id]
    )


class AnimeCollectionContent(CollectionContent):
    __mapper_args__ = {
        "polymorphic_identity": "anime",
        "eager_defaults": True,
    }

    content_id = mapped_column(
        ForeignKey("service_content_anime.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Anime"] = relationship(
        primaryjoin="Anime.id == AnimeCollectionContent.content_id",
        foreign_keys=[content_id],
        lazy="immediate",  # TODO: check if it is good idea
    )


class CharacterCollectionContent(CollectionContent):
    __mapper_args__ = {
        "polymorphic_identity": "character",
        "eager_defaults": True,
    }

    content_id = mapped_column(
        ForeignKey("service_content_characters.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Character"] = relationship(
        primaryjoin="Character.id == CharacterCollectionContent.content_id",
        foreign_keys=[content_id],
        lazy="immediate",  # TODO: check if it is good idea
    )


class PersonCollectionContent(CollectionContent):
    __mapper_args__ = {
        "polymorphic_identity": "person",
        "eager_defaults": True,
    }

    content_id = mapped_column(
        ForeignKey("service_content_people.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Person"] = relationship(
        primaryjoin="Person.id == PersonCollectionContent.content_id",
        foreign_keys=[content_id],
        lazy="immediate",  # TODO: check if it is good idea
    )


class MangaCollectionContent(CollectionContent):
    __mapper_args__ = {
        "polymorphic_identity": "manga",
        "eager_defaults": True,
    }

    content_id = mapped_column(
        ForeignKey("service_content_manga.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Manga"] = relationship(
        primaryjoin="Manga.id == MangaCollectionContent.content_id",
        foreign_keys=[content_id],
        lazy="immediate",  # TODO: check if it is good idea
    )


class NovelCollectionContent(CollectionContent):
    __mapper_args__ = {
        "polymorphic_identity": "novel",
        "eager_defaults": True,
    }

    content_id = mapped_column(
        ForeignKey("service_content_novel.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Novel"] = relationship(
        primaryjoin="Novel.id == NovelCollectionContent.content_id",
        foreign_keys=[content_id],
        lazy="immediate",  # TODO: check if it is good idea
    )
