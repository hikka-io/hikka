from app.common.utils.customization import is_valid_css_background
from client_requests import request_settings_customization
from client_requests import request_me_ui
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_settings_customization(
    client, create_test_user, get_test_token, test_session
):
    base = {
        "preferences": {
            "title_language": None,
            "name_language": None,
            "effects": None,
        },
        "styles": {
            "light": {
                "colors": {
                    "background": None,
                    "foreground": None,
                    "primary": None,
                    "primary_foreground": None,
                    "primary_border": None,
                    "secondary": None,
                    "secondary_foreground": None,
                    "muted": None,
                    "muted_foreground": None,
                    "accent_foreground": None,
                    "border": None,
                    "ring": None,
                    "popover": None,
                    "popover_foreground": None,
                    "sidebar_background": None,
                    "sidebar_foreground": None,
                    "sidebar_primary": None,
                    "sidebar_primary_foreground": None,
                    "sidebar_accent": None,
                    "sidebar_accent_foreground": None,
                    "sidebar_border": None,
                    "sidebar_ring": None,
                },
            },
            "dark": {
                "colors": {
                    "background": None,
                    "foreground": None,
                    "primary": None,
                    "primary_foreground": None,
                    "primary_border": None,
                    "secondary": None,
                    "secondary_foreground": None,
                    "muted": None,
                    "muted_foreground": None,
                    "accent_foreground": None,
                    "border": None,
                    "ring": None,
                    "popover": None,
                    "popover_foreground": None,
                    "sidebar_background": None,
                    "sidebar_foreground": None,
                    "sidebar_primary": None,
                    "sidebar_primary_foreground": None,
                    "sidebar_accent": None,
                    "sidebar_accent_foreground": None,
                    "sidebar_border": None,
                    "sidebar_ring": None,
                },
                "body": {
                    "background_image": None,
                },
            },
            "radius": None,
            "typography": {
                "h1": None,
                "h2": None,
                "h3": None,
                "h4": None,
                "h5": None,
                "p": None,
            },
        },
    }

    # Update customization
    response = await request_settings_customization(
        client, get_test_token, base
    )

    # Check whether changes has been applied
    assert response.status_code == status.HTTP_200_OK
    test_hls = {"h": 10, "l": 20, "s": 30}
    base["styles"]["dark"]["colors"]["background"] = test_hls
    base["preferences"]["title_language"] = "title_en"

    # Update customization once more
    response = await request_settings_customization(
        client, get_test_token, base
    )

    # Check once more
    assert response.status_code == status.HTTP_200_OK

    response = await request_me_ui(client, get_test_token)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["styles"]["dark"]["colors"]["background"] == test_hls
    assert response.json()["preferences"]["title_language"] == "title_en"

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_SETTINGS_CUSTOMIZATION
    assert log.user == create_test_user
    assert log.data["before"]["styles"]["dark"]["colors"]["background"] is None
    assert (
        log.data["after"]["styles"]["dark"]["colors"]["background"] == test_hls
    )


def test_valid_css_background():
    for css_value in [
        # Hex codes
        "#fff",
        "#FFF",
        "#000000",
        "#ABCDEF",
        "#ff000080",
        "#1234",
        # rgb/rgba functions
        "rgb(255, 0, 0)",
        "rgb(100%, 50%, 0%)",
        "rgba(255, 0, 0, 0.5)",
        "rgba(255, 255, 255, 1)",
        "RGB(0, 255, 0)",
        # hsl/hsla functions
        "hsl(120, 100%, 50%)",
        "hsl(0, 0%, 0%)",
        "hsla(240, 100%, 50%, 0.3)",
        "hsla(240, 100%, 50%, 1)",
        # Linear gradients
        "linear-gradient(red, yellow)",
        "linear-gradient(to right, red, orange)",
        "linear-gradient(45deg, blue, red)",
        "linear-gradient(0deg, blue, green 40%, red)",
        "repeating-linear-gradient(45deg, #3f87a6, #ebf8e1 15%)",
        # Radial gradients
        "radial-gradient(circle, red, yellow)",
        "radial-gradient(circle at 100%, #333, #333 50%, #eee 75%, #333 75%)",
        "repeating-radial-gradient(black, black 5px, white 5px, white 10px)",
        # Conic gradients
        "conic-gradient(from 45deg, red, orange)",
        "conic-gradient(red, orange, yellow, green, blue)",
        # Whitespace handling
        "  #ffffff  ",
        "rgb(  0  ,  255  ,  0  )",
        "linear-gradient(  to right  , red , blue )",
        # None
        None,
    ]:
        assert is_valid_css_background(css_value) is True


def test_invalid_css_background():
    for css_value in [
        # URLs
        "url('image.jpg')",
        'url("https://google.com/bad.png")',
        "url(/static/img.png)",
        "url(data:image/gif;base64,AAAA)",
        "src('font.woff')",  # src is sometimes used in other properties, check fallback
        # Dangerous stuff
        "javascript:alert(1)",
        "vbscript:msgbox(1)",
        "data:text/html,<script>alert(0)</script>",
        "file:///etc/passwd",
        "expression(alert(1))",
        # Invalid hex codes ---
        "#ZZZ",
        "#12",
        "#12345",
        "#123456789",
        "123456",
        "# 123456",
        # Syntax errors
        "linear-gradient(red, blue",
        "rgb(255, 0, 0",
        "linear-gradient",
        "gradient(red, blue)",
        # CSS injection
        "red; background-image: url('x')",
        "burl(test.jpg)",
        # Important breaks stuff (sup DustTail)
        "#000000!important",
        # Garbage
        "",
        "   ",
        "some-random-string",
    ]:
        assert is_valid_css_background(css_value) is False
