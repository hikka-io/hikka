from app.database import sessionmanager
from app.service import create_log
from app.utils import get_settings
from sqlalchemy import select
from app.models import User
from app import constants
import asyncio
import copy
import math


def hue_to_rgb(p, q, t):
    t = t % 1.0

    if t < 1 / 6:
        return p + (q - p) * 6 * t

    if t < 1 / 2:
        return q

    if t < 2 / 3:
        return p + (q - p) * (2 / 3 - t) * 6

    return p


def hsl_to_rgb(h, s, l):  # noqa: E741
    h = (h % 360) / 360
    s = s / 100
    l = l / 100  # noqa: E741

    if s == 0:
        return (l, l, l)

    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q

    return (
        hue_to_rgb(p, q, h + 1 / 3),
        hue_to_rgb(p, q, h),
        hue_to_rgb(p, q, h - 1 / 3),
    )


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hsl_to_oklch(color):
    if not isinstance(color, dict):
        return None

    if any(color.get(key) is None for key in ("h", "s", "l")):
        return None

    r, g, b = (
        srgb_to_linear(channel)
        for channel in hsl_to_rgb(color["h"], color["s"], color["l"])
    )

    # sRGB -> LMS (Björn Ottosson's OKLab matrices)
    long = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    medium = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    short = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b

    long, medium, short = (
        math.copysign(abs(value) ** (1 / 3), value)
        for value in (long, medium, short)
    )

    lightness = (
        0.2104542553 * long + 0.7936177850 * medium - 0.0040720468 * short
    )
    green_red = (
        1.9779984951 * long - 2.4285922050 * medium + 0.4505937099 * short
    )
    blue_yellow = (
        0.0259040371 * long + 0.7827717662 * medium - 0.8086757660 * short
    )

    chroma = math.sqrt(green_red**2 + blue_yellow**2)
    hue = math.degrees(math.atan2(blue_yellow, green_red)) % 360

    # Hue is meaningless for greys and only adds float noise
    if chroma < 1e-4:
        chroma = 0.0
        hue = 0.0

    return {
        "l": round(min(max(lightness, 0), 1), 4),
        "c": round(min(max(chroma, 0), 0.4), 4),
        "h": round(hue, 2),
    }


async def fix_migrate_customization():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        users = await session.scalars(select(User))

        for user in users:
            if (
                "dark" in user.styles
                and user.styles["dark"] is not None
                and "colors" in user.styles["dark"]
                and "primary_foreground" in user.styles["dark"]["colors"]
                and user.styles["dark"]["colors"]["primary_foreground"]
                is not None
            ):
                if (
                    "brand" in user.styles and user.styles["brand"]
                ) is None or "brand" not in user.styles:
                    brand_color = hsl_to_oklch(
                        user.styles["dark"]["colors"]["primary_foreground"]
                    )

                    log_before = {
                        "preferences": user.preferences,
                        "styles": user.styles,
                    }

                    user.styles = copy.deepcopy(user.styles)
                    user.styles["brand"] = brand_color

                    log_after = {
                        "preferences": user.preferences,
                        "styles": user.styles,
                    }

                    await session.commit()

                    if log_before != log_after:
                        await create_log(
                            session,
                            constants.LOG_SETTINGS_CUSTOMIZATION,
                            user,
                            data={"before": log_before, "after": log_after},
                        )

                    print(f"Updated user brand for {user.username}")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_migrate_customization())
