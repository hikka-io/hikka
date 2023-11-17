from sqlalchemy.dialects.postgresql import JSONB
from ..mixins import CreatedMixin, UpdatedMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from ..base import Base
from uuid import UUID


class Edit(
    Base,
    CreatedMixin,
    UpdatedMixin,
):
    __tablename__ = "service_edits"
    __mapper_args__ = {
        "polymorphic_identity": "default",
        "polymorphic_on": "content_type",
    }

    description: Mapped[str] = mapped_column(nullable=True)
    hidden: Mapped[bool] = mapped_column(default=False)
    content_type: Mapped[str]
    status: Mapped[str]

    edit_id: Mapped[int] = mapped_column(
        unique=True, index=True, autoincrement=True, primary_key=True
    )

    before: Mapped[dict] = mapped_column(JSONB, nullable=True)
    after: Mapped[dict] = mapped_column(JSONB)

    moderator_id = mapped_column(ForeignKey("service_users.id"))
    author_id = mapped_column(ForeignKey("service_users.id"))

    moderator: Mapped["User"] = relationship(
        back_populates="decisions",
        foreign_keys=[moderator_id],
        lazy="selectin",
    )

    author: Mapped["User"] = relationship(
        back_populates="edits",
        foreign_keys=[author_id],
        lazy="selectin",
    )

    content_id: Mapped[UUID]


class AnimeEdit(Edit):
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
        primaryjoin="Anime.id == AnimeEdit.content_id",
        foreign_keys=[content_id],
        lazy="immediate",  # ToDo: check if it is good idea
    )

    # @hybrid_property
    # def slug(self):
    #     return self.content.slug


class PersonEdit(Edit):
    __mapper_args__ = {"polymorphic_identity": "person"}

    content_id = mapped_column(
        ForeignKey("service_content_people.id", ondelete="CASCADE"),
        use_existing_column=True,
        index=True,
    )

    content: Mapped["Person"] = relationship(
        primaryjoin="Person.id == PersonEdit.content_id",
        foreign_keys=[content_id],
        lazy="immediate",  # ToDo: check if it is good idea
    )

    # @hybrid_property
    # def slug(self):
    #     return self.content.slug
