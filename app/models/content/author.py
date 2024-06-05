from ..association import manga_author_roles_association_table
from ..association import novel_author_roles_association_table
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from ..mixins import SlugMixin
from ..base import Base


class AuthorRole(Base, SlugMixin):
    __tablename__ = "service_content_author_roles"

    name_en: Mapped[str] = mapped_column(nullable=True)
    name_ua: Mapped[str] = mapped_column(nullable=True)
    weight: Mapped[int] = mapped_column(nullable=True)

    manga_authors: Mapped[list["MangaAuthor"]] = relationship(
        secondary=manga_author_roles_association_table,
        back_populates="roles",
        viewonly=True,
    )

    novel_authors: Mapped[list["NovelAuthor"]] = relationship(
        secondary=novel_author_roles_association_table,
        back_populates="roles",
        viewonly=True,
    )


class MangaAuthor(Base):
    __tablename__ = "service_content_manga_authors"

    roles: Mapped[list["AuthorRole"]] = relationship(
        secondary=manga_author_roles_association_table,
        order_by="AuthorRole.weight.desc()",
        back_populates="manga_authors",
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
        back_populates="manga_author_roles", foreign_keys=[person_id]
    )

    manga: Mapped["Manga"] = relationship(
        back_populates="authors", foreign_keys=[manga_id]
    )

    unique_constraint = UniqueConstraint(person_id, manga_id)


class NovelAuthor(Base):
    __tablename__ = "service_content_novel_authors"

    roles: Mapped[list["AuthorRole"]] = relationship(
        secondary=novel_author_roles_association_table,
        order_by="AuthorRole.weight.desc()",
        back_populates="novel_authors",
        lazy="joined",
    )

    person_id = mapped_column(
        ForeignKey("service_content_people.id"),
        index=True,
    )

    novel_id = mapped_column(
        ForeignKey("service_content_novel.id"),
        index=True,
    )

    person: Mapped["Person"] = relationship(
        back_populates="novel_author_roles", foreign_keys=[person_id]
    )

    novel: Mapped["Novel"] = relationship(
        back_populates="authors", foreign_keys=[novel_id]
    )

    unique_constraint = UniqueConstraint(person_id, novel_id)
