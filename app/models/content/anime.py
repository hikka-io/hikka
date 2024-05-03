from ..association import anime_genres_association_table
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import query_expression
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from datetime import datetime
from ..base import Base

from ..mixins import (
    NeedsSearchUpdateMixin,
    IgnoredFieldsMixin,
    SynonymsMixin,
    ContentMixin,
    UpdatedMixin,
    SlugMixin,
)


class Anime(
    Base,
    SlugMixin,
    ContentMixin,
    UpdatedMixin,
    SynonymsMixin,
    IgnoredFieldsMixin,
    NeedsSearchUpdateMixin,
):
    __tablename__ = "service_content_anime"

    favourite_created: Mapped[datetime] = query_expression()
    comments_count: Mapped[int] = query_expression()

    # Multilang fields
    title_ja: Mapped[str] = mapped_column(String(255), nullable=True)
    title_en: Mapped[str] = mapped_column(String(255), nullable=True)
    title_ua: Mapped[str] = mapped_column(String(255), nullable=True)
    synopsis_en: Mapped[str] = mapped_column(nullable=True)
    synopsis_ua: Mapped[str] = mapped_column(nullable=True)

    # Service fields
    aggregator_updated: Mapped[datetime] = mapped_column(nullable=True)
    airing_seasons: Mapped[list] = mapped_column(JSONB, default=[])
    mal_id: Mapped[int] = mapped_column(index=True, nullable=True)
    translated_ua: Mapped[bool] = mapped_column(default=False)
    needs_update: Mapped[bool] = mapped_column(default=False)

    # Metadata
    rating: Mapped[str] = mapped_column(String(16), index=True, nullable=True)
    source: Mapped[str] = mapped_column(String(16), index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(16), index=True, nullable=True)
    season: Mapped[str] = mapped_column(String(6), index=True, nullable=True)
    episodes_released: Mapped[int] = mapped_column(nullable=True)
    year: Mapped[int] = mapped_column(index=True, nullable=True)
    start_date: Mapped[datetime] = mapped_column(nullable=True)
    episodes_total: Mapped[int] = mapped_column(nullable=True)
    end_date: Mapped[datetime] = mapped_column(nullable=True)
    duration: Mapped[int] = mapped_column(nullable=True)
    nsfw: Mapped[bool] = mapped_column(nullable=True)
    scored_by: Mapped[int] = mapped_column(default=0)
    score: Mapped[float] = mapped_column(default=0)
    media_type: Mapped[str] = mapped_column(
        String(16), index=True, nullable=True
    )

    schedule: Mapped[list] = mapped_column(JSONB, default=[])
    external: Mapped[list] = mapped_column(JSONB, default=[])
    videos: Mapped[list] = mapped_column(JSONB, default=[])
    stats: Mapped[list] = mapped_column(JSONB, default=[])
    ost: Mapped[list] = mapped_column(JSONB, default=[])

    voices: Mapped[list["AnimeVoice"]] = relationship(
        back_populates="anime", viewonly=True
    )

    staff: Mapped[list["AnimeStaff"]] = relationship(
        back_populates="anime", viewonly=True
    )

    episodes_list: Mapped[list["AnimeEpisode"]] = relationship(
        back_populates="anime", viewonly=True
    )

    characters: Mapped[list["AnimeCharacter"]] = relationship(
        back_populates="anime", viewonly=True
    )

    recommendations: Mapped[list["AnimeRecommendation"]] = relationship(
        foreign_keys="[AnimeRecommendation.anime_id]",
        back_populates="anime",
        viewonly=True,
    )

    genres: Mapped[list["AnimeGenre"]] = relationship(
        secondary=anime_genres_association_table, back_populates="anime"
    )

    companies: Mapped[list["CompanyAnime"]] = relationship(
        back_populates="anime", viewonly=True
    )

    watch: Mapped[list["AnimeWatch"]] = relationship(
        foreign_keys="[AnimeWatch.anime_id]",
        back_populates="anime",
    )

    poster_id = mapped_column(
        ForeignKey("service_images.id", ondelete="SET NULL"), index=True
    )

    poster_relation: Mapped["Image"] = relationship(lazy="selectin")

    franchise_id = mapped_column(
        ForeignKey("service_content_anime_franchises.id", ondelete="SET NULL"),
        index=True,
    )

    franchise_relation: Mapped["AnimeFranchise"] = relationship(
        back_populates="anime", foreign_keys=[franchise_id]
    )

    # TODO: Check AssociationProxy
    # https://docs.sqlalchemy.org/en/20/orm/extensions/associationproxy.html
    producers: Mapped[list["Company"]] = relationship(
        secondary="service_content_companies_anime",
        primaryjoin="Anime.id == CompanyAnime.anime_id",
        secondaryjoin=(
            "and_("
            "CompanyAnime.company_id == Company.id,"
            "CompanyAnime.type == 'producer')"
        ),
        viewonly=True,
    )

    studios: Mapped[list["Company"]] = relationship(
        secondary="service_content_companies_anime",
        primaryjoin="Anime.id == CompanyAnime.anime_id",
        secondaryjoin=(
            "and_("
            "CompanyAnime.company_id == Company.id,"
            "CompanyAnime.type == 'studio')"
        ),
        viewonly=True,
    )

    # Very dirty hacks, but they do the trick
    @hybrid_property
    def poster(self):
        if not self.poster_relation:
            return None

        if self.poster_relation.ignore or not self.poster_relation.uploaded:
            return None

        return self.poster_relation.url

    @hybrid_property
    def has_franchise(self):
        return self.franchise_id is not None

    @hybrid_property
    def data_type(self):
        return "anime"
