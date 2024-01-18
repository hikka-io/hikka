from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import String
from datetime import datetime


class NeedsSearchUpdateMixin:
    needs_search_update: Mapped[bool] = mapped_column(default=False)


class ContentMixin:
    content_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)


class SlugMixin:
    slug: Mapped[str] = mapped_column(String(255), index=True)


class UpdatedMixin:
    updated: Mapped[datetime]


class CreatedMixin:
    created: Mapped[datetime]


class FavoritesMixin:
    favorites: Mapped[int] = mapped_column(default=0)


class NamesMixin:
    name_ja: Mapped[str] = mapped_column(nullable=True)
    name_en: Mapped[str] = mapped_column(nullable=True)
    name_ua: Mapped[str] = mapped_column(nullable=True)


class TitlesMixin:
    title_ja: Mapped[str] = mapped_column(nullable=True)
    title_en: Mapped[str] = mapped_column(nullable=True)
    title_ua: Mapped[str] = mapped_column(nullable=True)


# https://amercader.net/blog/beware-of-json-fields-in-sqlalchemy/
# no longer using a JSON here but the mutability bit still applies
class IgnoredFieldsMixin:
    ignored_fields: Mapped[MutableList] = mapped_column(
        MutableList.as_mutable(JSONB), default=[]
    )
