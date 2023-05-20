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

anime_studios_association_table = Table(
    "service_relation_anime_studios",
    Base.metadata,
    Column(
        "anime_id",
        ForeignKey("service_content_anime.id"),
        primary_key=True,
    ),
    Column(
        "company_id",
        ForeignKey("service_content_companies.id"),
        primary_key=True,
    ),
)

anime_producers_association_table = Table(
    "service_relation_anime_producers",
    Base.metadata,
    Column(
        "anime_id",
        ForeignKey("service_content_anime.id"),
        primary_key=True,
    ),
    Column(
        "company_id",
        ForeignKey("service_content_companies.id"),
        primary_key=True,
    ),
)
