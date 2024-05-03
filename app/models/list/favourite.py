from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from ..mixins import CreatedMixin
from ..base import Base
from uuid import UUID


class Favourite(Base, CreatedMixin):
    __tablename__ = "service_favourite"
    __mapper_args__ = {
        "polymorphic_identity": "default",
        "polymorphic_on": "content_type",
    }

    content_type: Mapped[str]
    content_id: Mapped[UUID]

    user_id = mapped_column(ForeignKey("service_users.id"))
    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class AnimeFavourite(Favourite):
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
        primaryjoin="Anime.id == AnimeFavourite.content_id",
        foreign_keys=[content_id],
        lazy="immediate",  # TODO: check if it is good idea
    )

    # TODO: remove me
    anime: Mapped["Anime"] = relationship(
        primaryjoin="Anime.id == AnimeFavourite.content_id",
        foreign_keys=[content_id],
        lazy="immediate",  # TODO: check if it is good idea
        viewonly=True,
    )


class CollectionFavourite(Favourite):
    __mapper_args__ = {
        "polymorphic_identity": "collection",
        "eager_defaults": True,
    }

    content_id = mapped_column(
        ForeignKey("service_collections.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Collection"] = relationship(
        primaryjoin="Collection.id == CollectionFavourite.content_id",
        foreign_keys=[content_id],
        lazy="immediate",  # TODO: check if it is good idea
    )


class CharacterFavourite(Favourite):
    __mapper_args__ = {
        "polymorphic_identity": "character",
        "eager_defaults": True,
    }

    content_id = mapped_column(
        ForeignKey("service_characters.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Character"] = relationship(
        primaryjoin="Character.id == CharacterFavourite.content_id",
        foreign_keys=[content_id],
        lazy="immediate",  # TODO: check if it is good idea
    )
