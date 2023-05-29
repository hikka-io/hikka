from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from ..mixins import ContentMixin
from datetime import datetime
from ..base import Base


class AnimeFranchise(Base, ContentMixin):
    __tablename__ = "service_content_anime_franchises"

    updated: Mapped[datetime] = mapped_column(nullable=True)
    scored_by: Mapped[int] = mapped_column(default=0)
    score: Mapped[float] = mapped_column(default=0)

    anime: Mapped[list["Anime"]] = relationship(
        back_populates="franchise_relation"
    )
