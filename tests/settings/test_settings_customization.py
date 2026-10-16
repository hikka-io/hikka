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
            "overrides": {"light": None, "dark": None},
            "brand": None,
            "radius": None,
        },
    }

    # Update customization
    response = await request_settings_customization(
        client, get_test_token, base
    )

    # Check whether changes has been applied
    assert response.status_code == status.HTTP_200_OK
    test_oklch = {"l": 0.2, "c": 0.1, "h": 120}
    base["styles"]["overrides"]["dark"] = {"background": test_oklch}
    base["styles"]["radius"] = "0.75rem"
    base["preferences"]["title_language"] = "title_en"

    # Update customization once more
    response = await request_settings_customization(
        client, get_test_token, base
    )

    # Check once more
    assert response.status_code == status.HTTP_200_OK

    response = await request_me_ui(client, get_test_token)
    styles = response.json()["styles"]
    assert response.status_code == status.HTTP_200_OK
    assert styles["overrides"]["dark"]["background"] == test_oklch
    assert styles["radius"] == "0.75rem"
    assert response.json()["preferences"]["title_language"] == "title_en"

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_SETTINGS_CUSTOMIZATION
    assert log.user == create_test_user
    assert log.data["before"]["styles"]["overrides"]["dark"] is None
    assert (
        log.data["after"]["styles"]["overrides"]["dark"]["background"]
        == test_oklch
    )


async def test_settings_customization_home_widgets(
    client, create_test_user, get_test_token, test_session
):
    # Update customization
    response = await request_settings_customization(
        client,
        get_test_token,
        {
            "styles": {},
            "preferences": {
                "home_widgets": ["tracker", "history", "ongoings", "schedule"],
            },
        },
    )

    # Check whether changes has been applied
    assert response.status_code == status.HTTP_200_OK

    response = await request_me_ui(client, get_test_token)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["preferences"]["home_widgets"] == [
        "tracker",
        "history",
        "ongoings",
        "schedule",
    ]

    response = await request_settings_customization(
        client,
        get_test_token,
        {
            "styles": {},
            "preferences": {
                "home_widgets": ["tracker", "ongoings", "schedule"],
            },
        },
    )

    response = await request_me_ui(client, get_test_token)
    assert response.json()["preferences"]["home_widgets"] == [
        "tracker",
        "ongoings",
        "schedule",
    ]

    response = await request_settings_customization(
        client,
        get_test_token,
        {
            "styles": {},
            "preferences": {"home_widgets": []},
        },
    )

    response = await request_me_ui(client, get_test_token)
    assert response.json()["preferences"]["home_widgets"] == []

    # Update customization
    response = await request_settings_customization(
        client,
        get_test_token,
        {
            "styles": {},
            "preferences": {
                "home_widgets": ["tracker", "tracker"],
            },
        },
    )

    # Check whether changes has been applied
    assert response.status_code == status.HTTP_400_BAD_REQUEST
