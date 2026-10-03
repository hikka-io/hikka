from client_requests import request_settings_links
from client_requests import request_me
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_settings_links_bad(client, create_test_user, get_test_token):
    # Make sure we don't bad links for specific socials
    for social in [
        "instagram",
        "telegram",
        "threads",
        "twitter",
        "discord",
        "bluesky",
        "github",
        "steam",
    ]:
        response = await request_settings_links(
            client,
            get_test_token,
            [{"url": "https://bad.link", "icon": social}],
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["code"] == "system:validation_error"

    # Ensure 10 links limit can't be bypassed
    response = await request_settings_links(
        client,
        get_test_token,
        [
            {
                "text": f"Link {index}",
                "url": f"https://link{index}.com",
                "icon": "custom",
            }
            for index in range(0, 11)
        ],
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_settings_links(
    client, create_test_user, get_test_token, test_session
):
    response = await request_me(client, get_test_token)
    assert response.json()["links"] == []

    links = [
        {"text": f"Link {icon}", "url": url, "icon": "custom"}
        for icon, url in {
            "fediverse": "https://social.noleron.com/@user",
            "steam": "https://steamcommunity.com/id/user/",
            "instagram": "https://www.instagram.com/user",
            "bluesky": "https://bsky.app/profile/user",
            "threads": "https://threads.com/@user",
            "twitter": "https://twitter.com/user",
            "discord": "https://discord.com/user",
            "github": "https://github.com/user",
            "custom": "https://user.website/",
            "telegram": "https://t.me/user",
        }.items()
    ]

    # Change links for user
    response = await request_settings_links(
        client,
        get_test_token,
        links,
    )

    # Now check if user links has been upated
    assert response.status_code == status.HTTP_200_OK

    response = await request_me(client, get_test_token)
    assert response.json()["links"] == links

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_SETTINGS_LINKS
    assert log.user == create_test_user
    assert log.data["before"] == []
    assert log.data["after"] == links
