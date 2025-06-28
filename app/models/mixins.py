from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import query_expression
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import validates
from sqlalchemy.orm import Mapped
from sqlalchemy import String
from datetime import datetime


class MyScoreMixin:
    @declared_attr
    def my_score(cls):
        return query_expression(expire_on_flush=False)


class DeletedMixin:
    deleted: Mapped[bool] = mapped_column(default=False, index=True)


class SynonymsMixin:
    synonyms: Mapped[list] = mapped_column(JSONB, default=[])


class NeedsSearchUpdateMixin:
    needs_search_update: Mapped[bool] = mapped_column(default=True)


class ContentMixin:
    content_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)


class SlugMixin:
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    @validates("slug")
    def ensure_lowercase(self, key, value):
        return value.lower()


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
