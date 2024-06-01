from ..association import manga_magazines_association_table
from ..mixins import ContentMixin, SlugMixin
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from ..base import Base


class Magazine(Base, ContentMixin, SlugMixin):
    __tablename__ = "service_content_magazines"

    mal_id: Mapped[int] = mapped_column(index=True, nullable=True)
    name: Mapped[str]

    manga: Mapped[list["Manga"]] = relationship(
        secondary=manga_magazines_association_table,
        back_populates="magazines",
    )
