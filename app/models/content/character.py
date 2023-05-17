from sqlalchemy import ForeignKey, UniqueConstraint
from ..mixins import ContentMixin, SlugMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import String
from datetime import datetime
from ..base import Base


class Character(Base, ContentMixin, SlugMixin):
    __tablename__ = "service_content_characters"

    name_ja: Mapped[str] = mapped_column(String(255), nullable=True)
    name_en: Mapped[str] = mapped_column(String(255), nullable=True)
    name_ua: Mapped[str] = mapped_column(String(255), nullable=True)

    favorites: Mapped[int] = mapped_column(default=0, nullable=True)
    updated: Mapped[datetime]


# class AnimeCharacter(Base, SlugMixin):
#     __tablename__ = "service_content_anime_characters"

#     main: Mapped[bool]

#     unique_constraint = UniqueConstraint(followed_user_id, user_id)

# anime: fields.ForeignKeyRelation["Anime"] = fields.ForeignKeyField(
#     "models.Anime", related_name="characters"
# )

# class Meta:
#     table = "service_content_anime_characters"

#     unique_together = ("anime", "character")
