from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from ..base import Base


class AnimeRecommendation(Base):
    __tablename__ = "service_content_anime_recommendations"

    weight: Mapped[int]

    recommendation_id: Mapped[int] = relationship(
        ForeignKey("service_content_anime.id"),
    )

    anime_id: Mapped[int] = relationship(
        ForeignKey("service_content_anime.id"),
    )

    recommendation: Mapped["Anime"] = relationship(
        back_populates="recommended_to", foreign_keys=[recommendation_id]
    )

    anime: Mapped["User"] = relationship(
        back_populates="recommendation", foreign_keys=[anime_id]
    )

    unique_constraint = UniqueConstraint(recommendation_id, anime_id)
