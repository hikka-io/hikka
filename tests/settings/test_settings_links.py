from client_requests import request_settings_links
from client_requests import request_me
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_settings_links_bad(client, create_test_user, get_test_token):
    # Ensure 10 links limit can't be bypassed
    response = await request_settings_links(
        client,
        get_test_token,
        [
            {
                "text": f"Link {index}",
                "url": f"https://link{index}.com",
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

    batches = [
        {
            "https://social.noleron.com/@user": "custom",
            "https://steamcommunity.com/id/user/": "steam",
            "https://www.instagram.com/user": "instagram",
            "https://bsky.app/profile/user": "bluesky",
            "https://threads.com/@user": "threads",
            "https://twitter.com/user": "twitter",
            "https://discord.com/user": "discord",
            "https://github.com/user": "github",
            "https://user.website/": "custom",
            "https://t.me/user": "telegram",
        },
        {
            "https://www.youtube.com/@user": "youtube",
            "https://zenko.online/users/user": "zenko",
            "https://www.reddit.com/user/user": "reddit",
            "https://www.chess.com/member/user": "chess",
            "https://mangalist.in.ua/user": "mangalist",
            "https://anitube.in.ua/user": "anitube",
            "https://manga.in.ua/user": "mangainua",
            "https://dgmanga.app/user": "dgmanga",
            "https://youtu.be/video": "youtube",
            "https://mikai.me/user": "mikai",
        },
    ]

    previous_links = []

    for expected_icons in batches:
        links = [
            {"text": f"Link {index}", "url": url}
            for index, url in enumerate(expected_icons)
        ]

        expected_links = [
            {
                "text": link["text"],
                "url": link["url"],
                "icon": expected_icons[link["url"]],
            }
            for link in links
        ]

        # Change links for user
        response = await request_settings_links(
            client,
            get_test_token,
            links,
        )

        # Now check if user links has been upated
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["links"] == expected_links
        assert "password_hash" not in response.json()

        response = await request_me(client, get_test_token)
        assert response.json()["links"] == expected_links

        # Check log
        log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
        assert log.log_type == constants.LOG_SETTINGS_LINKS
        assert log.user == create_test_user
        assert log.data["before"] == previous_links
        assert log.data["after"] == expected_links

        previous_links = expected_links
