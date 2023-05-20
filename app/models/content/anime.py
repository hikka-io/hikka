from ..association import anime_producers_association_table
from ..association import anime_studios_association_table
from ..association import anime_genres_association_table
from sqlalchemy.dialects.postgresql import JSONB
from ..mixins import ContentMixin, SlugMixin
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
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
    nsfw: Mapped[bool] = mapped_column(nullable=True)
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

    franchise_id = mapped_column(
        ForeignKey("service_content_anime_franchises.id", ondelete="SET NULL")
    )

    franchise: Mapped["AnimeFranchise"] = relationship(
        back_populates="anime", foreign_keys=[franchise_id]
    )

    voices: Mapped[list["AnimeVoice"]] = relationship(back_populates="anime")
    staff: Mapped[list["AnimeStaff"]] = relationship(back_populates="anime")

    episodes_list: Mapped[list["AnimeEpisode"]] = relationship(
        back_populates="anime"
    )

    characters: Mapped[list["AnimeCharacter"]] = relationship(
        back_populates="anime"
    )

    recommendations: Mapped[list["AnimeRecommendation"]] = relationship(
        foreign_keys="[AnimeRecommendation.anime_id]",
        back_populates="anime",
    )

    recommended_to: Mapped[list["AnimeRecommendation"]] = relationship(
        foreign_keys="[AnimeRecommendation.recommendation_id]",
        back_populates="recommendation",
    )

    genres: Mapped[list["AnimeGenre"]] = relationship(
        secondary=anime_genres_association_table, back_populates="anime"
    )

    producers: Mapped[list["Company"]] = relationship(
        secondary=anime_producers_association_table,
        back_populates="producer_anime",
    )

    studios: Mapped[list["Company"]] = relationship(
        secondary=anime_studios_association_table,
        back_populates="studio_anime",
    )

    favourite: Mapped[list["AnimeFavourite"]] = relationship(
        foreign_keys="[AnimeFavourite.anime_id]",
        back_populates="anime",
    )

    watch: Mapped[list["AnimeWatch"]] = relationship(
        foreign_keys="[AnimeWatch.anime_id]",
        back_populates="anime",
    )

    # ToDo: images
