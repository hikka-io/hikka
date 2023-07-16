from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped
from ..base import Base


class AnimeRecommendation(Base):
    __tablename__ = "service_content_anime_recommendations"

    weight: Mapped[int]

    recommendation_id = mapped_column(
        ForeignKey("service_content_anime.id"),
        index=True,
    )

    anime_id = mapped_column(
        ForeignKey("service_content_anime.id"),
        index=True,
    )

    recommendation: Mapped["Anime"] = relationship(
        back_populates="recommended_to", foreign_keys=[recommendation_id]
    )

    anime: Mapped["Anime"] = relationship(
        back_populates="recommendations", foreign_keys=[anime_id]
    )

    unique_constraint = UniqueConstraint(recommendation_id, anime_id)
