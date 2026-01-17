from client_requests import request_create_edit
from client_requests import request_edit_list
from fastapi import status


async def test_edit_create(
    client,
    aggregator_characters,
    aggregator_people,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    # Create edit for anime
    response = await request_create_edit(
        client,
        get_test_token,
        "anime",
        "bocchi-the-rock-9e172d",
        {
            "description": "Brief description",
            "after": {"title_en": "Bocchi The Rock!"},
        },
    )

    # Check status and data
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json()["created"], int)

    assert response.json()["before"]["title_en"] == "Bocchi the Rock!"
    assert response.json()["after"]["title_en"] == "Bocchi The Rock!"
    assert response.json()["description"] == "Brief description"
    assert response.json()["author"]["username"] == "testuser"
    assert response.json()["content_type"] == "anime"
    assert response.json()["status"] == "pending"
    assert response.json()["moderator"] is None
    assert response.json()["edit_id"] == 18

    # Now create one more edit for person
    response = await request_create_edit(
        client,
        get_test_token,
        "person",
        "justin-cook-77f1b3",
        {
            "after": {"name_ua": "Джастін Кук"},
        },
    )

    # Make sure we got correct response code
    assert response.status_code == status.HTTP_200_OK

    # And one more edit for character
    response = await request_create_edit(
        client,
        get_test_token,
        "character",
        "hitori-gotou-cadd70",
        {
            "after": {
                "description_ua": "Головна героїня аніме Самітниця рокер",
                "name_ua": "Ґото Хіторі",
            },
        },
    )

    # Make sure we got correct response code
    assert response.status_code == status.HTTP_200_OK
    # Fetch list of edits
    response = await request_edit_list(client)

    # It should return 200 status
    assert response.status_code == status.HTTP_200_OK

    # Some checks to verify order and content
    assert response.json()["list"][0]["edit_id"] == 20
    assert response.json()["list"][1]["edit_id"] == 19
    assert response.json()["list"][2]["edit_id"] == 18
    from pprint import pprint

    pprint(response.json())
    assert (
        response.json()["list"][0]["content"]["slug"] == "hitori-gotou-cadd70"
    )

    assert response.json()["list"][1]["content"]["slug"] == "justin-cook-77f1b3"
    assert (
        response.json()["list"][2]["content"]["slug"]
        == "bocchi-the-rock-9e172d"
    )
