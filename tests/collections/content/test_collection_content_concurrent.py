from client_requests import request_delete_collection_content
from client_requests import request_add_collection_content
from client_requests import request_collection_info
from fastapi import status
import asyncio


async def test_collection_content_concurrent(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_anime_collection,
    create_test_user,
    get_test_token,
):
    reference = await create_anime_collection(
        get_test_token,
        [
            ("fullmetal-alchemist-brotherhood-fc524a", "Good"),
            ("bocchi-the-rock-9e172d", "Great"),
        ],
        ["Good", "Great"],
    )

    # Parallel adds into one group keep orders consecutive
    responses = await asyncio.gather(
        *[
            request_add_collection_content(
                client, reference, get_test_token, slug, {"label": "Good"}
            )
            for slug in [
                "kimi-no-na-wa-945779",
                "oshi-no-ko-421060",
                "steinsgate-f29797",
            ]
        ]
    )

    assert [response.status_code for response in responses] == [
        status.HTTP_200_OK
    ] * 3

    # Double click adds the title only once
    responses = await asyncio.gather(
        *[
            request_add_collection_content(
                client,
                reference,
                get_test_token,
                "kaguya-sama-wa-kokurasetai-ultra-romantic-fcd761",
                {"label": "Great"},
            )
            for _ in range(2)
        ]
    )

    assert sorted(response.status_code for response in responses) == [
        status.HTTP_200_OK,
        status.HTTP_400_BAD_REQUEST,
    ]

    # Parallel deletes of one title remove it only once
    responses = await asyncio.gather(
        *[
            request_delete_collection_content(
                client, reference, get_test_token, "kimi-no-na-wa-945779"
            )
            for _ in range(2)
        ]
    )

    assert sorted(response.status_code for response in responses) == [
        status.HTTP_200_OK,
        status.HTTP_404_NOT_FOUND,
    ]

    response = await request_collection_info(client, reference)
    collection = response.json()["collection"]
    slugs = [entry["content"]["slug"] for entry in collection]

    assert response.json()["entries"] == len(collection) == 5
    assert len(set(slugs)) == len(slugs)
    assert [entry["order"] for entry in collection] == [1, 2, 3, 4, 5]
    assert [entry["label"] for entry in collection] == [
        "Good",
        "Good",
        "Good",
        "Great",
        "Great",
    ]
