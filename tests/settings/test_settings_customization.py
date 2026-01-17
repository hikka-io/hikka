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
