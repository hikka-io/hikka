from sqlalchemy import Table, Column, ForeignKey
from .base import Base

genres_anime_association_table = Table(
    "service_relation_genres_anime",
    Base.metadata,
    Column(
        "anime_id",
        ForeignKey("service_content_anime.id"),
        primary_key=True,
    ),
    Column(
        "genre_id",
        ForeignKey("service_content_genres.id"),
        primary_key=True,
    ),
)

genres_manga_association_table = Table(
    "service_relation_genres_manga",
    Base.metadata,
    Column(
        "manga_id",
        ForeignKey("service_content_manga.id"),
        primary_key=True,
    ),
    Column(
        "genre_id",
        ForeignKey("service_content_genres.id"),
        primary_key=True,
    ),
)

genres_novel_association_table = Table(
    "service_relation_genres_novel",
    Base.metadata,
    Column(
        "novel_id",
        ForeignKey("service_content_novel.id"),
        primary_key=True,
    ),
    Column(
        "genre_id",
        ForeignKey("service_content_genres.id"),
        primary_key=True,
    ),
)


anime_staff_roles_association_table = Table(
    "service_relation_anime_staff_roles",
    Base.metadata,
    Column(
        "staff_id",
        ForeignKey("service_content_anime_staff.id"),
        primary_key=True,
    ),
    Column(
        "role_id",
        ForeignKey("service_content_anime_staff_roles.id"),
        primary_key=True,
    ),
)

manga_magazines_association_table = Table(
    "service_relation_manga_magazines",
    Base.metadata,
    Column(
        "manga_id",
        ForeignKey("service_content_manga.id"),
        primary_key=True,
    ),
    Column(
        "magazine_id",
        ForeignKey("service_content_magazines.id"),
        primary_key=True,
    ),
)

novel_magazines_association_table = Table(
    "service_relation_novel_magazines",
    Base.metadata,
    Column(
        "novel_id",
        ForeignKey("service_content_novel.id"),
        primary_key=True,
    ),
    Column(
        "magazine_id",
        ForeignKey("service_content_magazines.id"),
        primary_key=True,
    ),
)

manga_author_roles_association_table = Table(
    "service_relation_manga_author_roles",
    Base.metadata,
    Column(
        "author_id",
        ForeignKey("service_content_manga_authors.id"),
        primary_key=True,
    ),
    Column(
        "role_id",
        ForeignKey("service_content_author_roles.id"),
        primary_key=True,
    ),
)

novel_author_roles_association_table = Table(
    "service_relation_novel_author_roles",
    Base.metadata,
    Column(
        "author_id",
        ForeignKey("service_content_novel_authors.id"),
        primary_key=True,
    ),
    Column(
        "role_id",
        ForeignKey("service_content_author_roles.id"),
        primary_key=True,
    ),
)
