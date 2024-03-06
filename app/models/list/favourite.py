from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from ..mixins import CreatedMixin
from ..base import Base
from uuid import UUID


class AnimeFavouriteLegacy(Base, CreatedMixin):
    __tablename__ = "service_favourite_anime"

    anime_id = mapped_column(ForeignKey("service_content_anime.id"))
    user_id = mapped_column(ForeignKey("service_users.id"))

    anime: Mapped["Anime"] = relationship(
        # back_populates="favourite",
        foreign_keys=[anime_id],
    )

    user: Mapped["User"] = relationship(
        # back_populates="favourite",
        foreign_keys=[user_id],
    )

    unique_constraint = UniqueConstraint(anime_id, user_id)


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

    anime: Mapped["Anime"] = relationship(
        primaryjoin="Anime.id == AnimeFavourite.content_id",
        foreign_keys=[content_id],
        # lazy="immediate",  # ToDo: check if it is good idea
    )
