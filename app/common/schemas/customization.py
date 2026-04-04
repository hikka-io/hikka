from app.common.utils.customization import is_valid_css_background
from pydantic import Field, field_validator
from app.schemas import CustomModel
from collections import defaultdict
from typing import List, Literal

from app.common.schemas.feed import (
    CollectionContentTypes,
    CommentContentTypes,
    ArticleContentTypes,
    ArticleCategories,
    FeedContentTypes,
)


class HSLColor(CustomModel):
    h: float = Field(ge=0, le=360)
    s: float = Field(ge=0, le=100)
    l: float = Field(ge=0, le=100)  # noqa: E741


class UIColorTokens(CustomModel):
    background: HSLColor | None = None
    foreground: HSLColor | None = None
    primary: HSLColor | None = None
    primary_foreground: HSLColor | None = None
    primary_border: HSLColor | None = None
    secondary: HSLColor | None = None
    secondary_foreground: HSLColor | None = None
    muted: HSLColor | None = None
    muted_foreground: HSLColor | None = None
    accent_foreground: HSLColor | None = None
    border: HSLColor | None = None
    ring: HSLColor | None = None
    popover: HSLColor | None = None
    popover_foreground: HSLColor | None = None
    sidebar_background: HSLColor | None = None
    sidebar_foreground: HSLColor | None = None
    sidebar_primary: HSLColor | None = None
    sidebar_primary_foreground: HSLColor | None = None
    sidebar_accent: HSLColor | None = None
    sidebar_accent_foreground: HSLColor | None = None
    sidebar_border: HSLColor | None = None
    sidebar_ring: HSLColor | None = None


class UIThemeStylesBody(CustomModel):
    background_image: str | None = None

    @field_validator("background_image")
    @classmethod
    def validate_background_image(cls, v):
        if not is_valid_css_background(v):
            raise ValueError("Only CSS gradients and color values are allowed")

        return v


class UIThemeStyles(CustomModel):
    colors: UIColorTokens | None = None
    body: UIThemeStylesBody | None = None


class UIStylesTypography(CustomModel):
    h1: str | None = None
    h2: str | None = None
    h3: str | None = None
    h4: str | None = None
    h5: str | None = None
    p: str | None = None


class UIStyles(CustomModel):
    dark: UIThemeStyles | None = None
    light: UIThemeStyles | None = None
    radius: str | None = Field(
        None,
    )
    typography: UIStylesTypography | None = None


UIEffect = Literal["snowfall"]
UIFeedWidgetOptions = Literal[
    "list", "profile", "feed", "tracker", "history", "ongoings", "schedule"
]


class UIFeedWidget(CustomModel):
    side: Literal["left", "center", "right"]
    slug: UIFeedWidgetOptions
    order: int


class UIFeedSettings(CustomModel):
    collection_content_types: list[CollectionContentTypes] | None = None
    comment_content_types: list[CommentContentTypes] | None = None
    article_content_types: list[ArticleContentTypes] | None = None
    article_categories: list[ArticleCategories] | None = None
    feed_content_types: list[FeedContentTypes] | None = None
    only_followed: bool = False

    widgets: list[UIFeedWidget] = [
        UIFeedWidget(side="left", slug="profile", order=1),
        UIFeedWidget(side="left", slug="tracker", order=2),
        UIFeedWidget(side="left", slug="history", order=3),
        UIFeedWidget(side="center", slug="ongoings", order=1),
        UIFeedWidget(side="center", slug="feed", order=2),
        UIFeedWidget(side="right", slug="schedule", order=1),
        UIFeedWidget(side="right", slug="list", order=2),
    ]

    @field_validator("widgets")
    @classmethod
    def validate_widgets(cls, widgets):
        # Slugs must be unique
        slugs = [w.slug for w in widgets]
        if len(slugs) != len(set(slugs)):
            raise ValueError("Widget slugs must be unique")

        # Orders must be unique per side and sequential starting from 1
        sides = defaultdict(list)
        for w in widgets:
            sides[w.side].append(w.order)

        for side, orders in sides.items():
            orders.sort()
            expected = list(range(1, len(orders) + 1))
            if orders != expected:
                raise ValueError(
                    f"Orders for side '{side}' must be sequential starting from 1"
                )

        return widgets


class UIPreferences(CustomModel):
    score: Literal["mal", "native"] | None = None
    effects: List[UIEffect] | None = None
    title_language: str | None = None
    name_language: str | None = None
    overlay: bool = True

    feed: UIFeedSettings = Field(default_factory=lambda: UIFeedSettings())

    # TODO: remove me later
    home_widgets: list[UIFeedWidgetOptions] = [
        "tracker",
        "history",
        "ongoings",
        "schedule",
    ]

    @field_validator("home_widgets")
    def validate_home_widgets(cls, widgets):
        if len(widgets) != len(set(widgets)):
            raise ValueError("Repeated widget not allowed")

        return widgets


class UserAppearance(CustomModel):
    styles: UIStyles | None = None
    preferences: UIPreferences | None = None


# Args
class UserCustomizationArgs(CustomModel):
    preferences: UIPreferences
    styles: UIStyles


# Responses
class UserCustomizationResponse(CustomModel):
    preferences: UIPreferences
    styles: UIStyles
