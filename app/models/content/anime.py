from ..association import anime_genres_association_table
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from ..mixins import ContentMixin, SlugMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import String
from datetime import datetime
from ..base import Base


class Anime(Base, ContentMixin, SlugMixin):
    __tablename__ = "service_content_anime"

    # Multilang fields
    title_ja: Mapped[str] = mapped_column(String(255), nullable=True)
    title_en: Mapped[str] = mapped_column(String(255), nullable=True)
    title_ua: Mapped[str] = mapped_column(String(255), nullable=True)
    synopsis_en: Mapped[str] = mapped_column(nullable=True)
    synopsis_ua: Mapped[str] = mapped_column(nullable=True)

    # Service fields
    needs_update: Mapped[bool] = mapped_column(default=False)
    updated: Mapped[datetime]

    # Metadata
    rating: Mapped[str] = mapped_column(String(16), index=True, nullable=True)
    source: Mapped[str] = mapped_column(String(16), index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(16), index=True, nullable=True)
    season: Mapped[str] = mapped_column(String(6), index=True, nullable=True)
    year: Mapped[int] = mapped_column(index=True, nullable=True)
    start_date: Mapped[datetime] = mapped_column(nullable=True)
    total_episodes: Mapped[int] = mapped_column(nullable=True)
    end_date: Mapped[datetime] = mapped_column(nullable=True)
    duration: Mapped[int] = mapped_column(nullable=True)
    episodes: Mapped[int] = mapped_column(nullable=True)
    score: Mapped[bool] = mapped_column(nullable=True)
    scored_by: Mapped[int] = mapped_column(default=0)
    score: Mapped[float] = mapped_column(default=0)
    media_type: Mapped[str] = mapped_column(
        String(16), index=True, nullable=True
    )

    translations: Mapped[dict] = mapped_column(JSONB, default=[])
    synonyms: Mapped[dict] = mapped_column(JSONB, default=[])
    external: Mapped[dict] = mapped_column(JSONB, default=[])
    videos: Mapped[dict] = mapped_column(JSONB, default=[])
    stats: Mapped[dict] = mapped_column(JSONB, default=[])
    ost: Mapped[dict] = mapped_column(JSONB, default=[])

    # ToDo: images

    genres: Mapped["AnimeGenre"] = relationship(
        secondary=anime_genres_association_table, back_populates="anime"
    )


# class Anime(Base):
#     studios: fields.ManyToManyRelation["Company"] = fields.ManyToManyField(
#         "models.Company",
#         related_name="studio_anime",
#         through="service_relation_anime_studios",
#     )

#     producers: fields.ManyToManyRelation["Company"] = fields.ManyToManyField(
#         "models.Company",
#         related_name="producer_anime",
#         through="service_relation_anime_producers",
#     )

#     franchise: fields.ForeignKeyRelation[
#         "AnimeFranchise"
#     ] = fields.ForeignKeyField(
#         "models.AnimeFranchise",
#         related_name="anime",
#         on_delete=fields.SET_NULL,
#         null=True,
#     )

#     recommendations: fields.ReverseRelation["AnimeRecommendation"]
#     recommended_to: fields.ReverseRelation["AnimeRecommendation"]

#     episodes_list: fields.ReverseRelation["AnimeEpisodes"]
#     characters: fields.ReverseRelation["AnimeCharacter"]
#     voices: fields.ReverseRelation["AnimeVoice"]
#     staff: fields.ReverseRelation["AnimeStaff"]

#     genres: fields.ManyToManyRelation["AnimeGenre"]

#     # images: fields.ReverseRelation["MALAnimeImage"]
