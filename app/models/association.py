from sqlalchemy import Table, Column, ForeignKey
from .base import Base

anime_genres_association_table = Table(
    "service_relation_anime_genres",
    Base.metadata,
    Column(
        "anime_id",
        ForeignKey("service_content_anime.id"),
        primary_key=True,
    ),
    Column(
        "genre_id",
        ForeignKey("service_content_anime_genres.id"),
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
