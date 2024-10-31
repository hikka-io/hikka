from pydantic import Field, field_validator
from app.utils import is_empty_markdown
from app.schemas import CustomModel
from app.utils import is_valid_tag
from app import constants
from enum import Enum


# Enums
class ArticleCategoryEnum(str, Enum):
    article_news = constants.ARTICLE_NEWS


# Args
class ArticleArgs(CustomModel):
    text: str = Field(min_length=3, max_length=65536)
    title: str = Field(min_length=3, max_length=255)
    tags: list[str] = Field(max_length=3)
    draft: bool = Field(default=True)
    category: ArticleCategoryEnum

    @field_validator("tags")
    def validate_tags(cls, tags):
        if not all([is_valid_tag(tag) for tag in tags]):
            raise ValueError("Invalid tag")

        return tags

    @field_validator("text")
    def validate_text(cls, text):
        if is_empty_markdown(text):
            raise ValueError("Field text consists of empty markdown")

        return text


# Responses
class ArticleResponse(CustomModel):
    cover: str | None
    tags: list[str]
    category: str
    draft: bool
    title: str
    text: str
    slug: str
