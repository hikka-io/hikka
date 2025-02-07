from ..association import tags_articles_association_table
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from ..base import Base


class Tag(Base):
    __tablename__ = "service_tags"
    __mapper_args__ = {
        "polymorphic_identity": "default",
        "polymorphic_on": "content_type",
    }

    content_count: Mapped[int] = mapped_column(default=0, index=True)
    category: Mapped[str] = mapped_column(index=True)
    name: Mapped[str] = mapped_column(index=True)
    content_type: Mapped[str]


class ArticleTag(Tag):
    __mapper_args__ = {"polymorphic_identity": "article"}

    articles: Mapped[list["Article"]] = relationship(
        secondary=tags_articles_association_table,
        back_populates="tags",
    )
