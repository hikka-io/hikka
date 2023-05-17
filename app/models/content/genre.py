from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import String
from datetime import datetime
from ..base import Base


class GenreMixing:
    name_en: Mapped[str] = mapped_column(String(64), nullable=True)
    name_ua: Mapped[str] = mapped_column(String(64), nullable=True)

    content_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    type: Mapped[str] = mapped_column(String(32))


class AnimeGenre(Base, GenreMixing):
    __tablename__ = "service_content_anime_genres"

    # anime: fields.ManyToManyRelation["Anime"] = fields.ManyToManyField(
    #     "models.Anime",
    #     related_name="genres",
    #     through="service_relation_anime_genres",
    # )
