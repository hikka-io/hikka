from pydantic import Field, field_validator
from app.schemas import CustomModel
from typing import List, Literal
import re


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
        if v is None:
            return v

        url_patterns = [
            r"https?://",  # http:// or https://
            r"www\.",  # www.
            r"url\(",  # CSS url() function
            r"//[a-zA-Z0-9]",  # Protocol-relative URLs like //cdn.com
        ]

        for pattern in url_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(
                    "URLs and links are not allowed in background_image"
                )

        allowed_patterns = [
            r"^linear-gradient\(",
            r"^radial-gradient\(",
            r"^repeating-linear-gradient\(",
            r"^repeating-radial-gradient\(",
            r"^conic-gradient\(",
            r"^#[0-9a-fA-F]{3,8}$",
            r"^rgb\(",
            r"^rgba\(",
            r"^hsl\(",
            r"^hsla\(",
        ]

        if not any(re.match(pattern, v) for pattern in allowed_patterns):
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


class UIPreferences(CustomModel):
    title_language: str | None = None
    name_language: str | None = None
    effects: List[UIEffect] | None = None


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
