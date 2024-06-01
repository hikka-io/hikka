from ..association import manga_author_roles_association_table
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from ..mixins import SlugMixin
from ..base import Base


class MangaAuthorRole(Base, SlugMixin):
    __tablename__ = "service_content_manga_author_roles"

    name_en: Mapped[str] = mapped_column(nullable=True)
    name_ua: Mapped[str] = mapped_column(nullable=True)
    weight: Mapped[int] = mapped_column(nullable=True)

    author: Mapped[list["MangaAuthor"]] = relationship(
        secondary=manga_author_roles_association_table,
        back_populates="roles",
        viewonly=True,
    )


class MangaAuthor(Base):
    __tablename__ = "service_content_manga_authors"

    roles: Mapped[list["MangaAuthorRole"]] = relationship(
        secondary=manga_author_roles_association_table,
        order_by="MangaAuthorRole.weight.desc()",
        back_populates="author",
        lazy="joined",
    )

    person_id = mapped_column(
        ForeignKey("service_content_people.id"),
        index=True,
    )

    manga_id = mapped_column(
        ForeignKey("service_content_manga.id"),
        index=True,
    )

    person: Mapped["Person"] = relationship(
        back_populates="author_roles", foreign_keys=[person_id]
    )

    manga: Mapped["Manga"] = relationship(
        back_populates="authors", foreign_keys=[manga_id]
    )

    unique_constraint = UniqueConstraint(person_id, manga_id)
