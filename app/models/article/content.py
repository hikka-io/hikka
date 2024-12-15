from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from ..base import Base
from uuid import UUID


class ArticleContent(Base):
    __tablename__ = "service_articles_content"

    content_type: Mapped[str]
    content_id: Mapped[UUID]

    article_id: Mapped[int] = mapped_column(
        ForeignKey("service_articles.id"), nullable=False
    )

    article: Mapped["Article"] = relationship(
        back_populates="content",
    )
