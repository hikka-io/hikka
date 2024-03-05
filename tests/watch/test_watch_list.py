from client_requests import request_watch_delete
from client_requests import request_watch_list
from client_requests import request_watch_add
from fastapi import status


async def test_watch_list(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
):
    # User watch list should be empty when we start
    response = await request_watch_list(client, "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 0

    # Add anime to watch list
    await request_watch_add(
        client,
        "bocchi-the-rock-9e172d",
        get_test_token,
        {
            "status": "watching",
            "episodes": 1,
            "score": 8,
        },
    )

    response = await request_watch_list(client, "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["status"] == "watching"
    assert (
        response.json()["list"][0]["anime"]["slug"] == "bocchi-the-rock-9e172d"
    )

    # Add one more anime to watch list
    await request_watch_add(
        client,
        "oshi-no-ko-421060",
        get_test_token,
        {
            "status": "planned",
            "episodes": 0,
            "score": 0,
        },
    )

    response = await request_watch_list(client, "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 2
    assert response.json()["list"][0]["status"] == "watching"
    assert response.json()["list"][1]["status"] == "planned"
    assert (
        response.json()["list"][0]["anime"]["slug"] == "bocchi-the-rock-9e172d"
    )
    assert response.json()["list"][1]["anime"]["slug"] == "oshi-no-ko-421060"

    # Try filtering by watch entry staus
    response = await request_watch_list(
        client, "testuser", {"watch_status": "watching"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["status"] == "watching"
    assert (
        response.json()["list"][0]["anime"]["slug"] == "bocchi-the-rock-9e172d"
    )

    # And now delete Bocchi from user's watch list
    await request_watch_delete(client, "bocchi-the-rock-9e172d", get_test_token)

    response = await request_watch_list(client, "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["status"] == "planned"
    assert response.json()["list"][0]["anime"]["slug"] == "oshi-no-ko-421060"


async def test_watch_list_order(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
):
    # ToDo: this test ideally should be split into bunch of smaller tests

    # Add Bocchi to watch list
    await request_watch_add(
        client,
        "bocchi-the-rock-9e172d",
        get_test_token,
        {
            "status": "watching",
            "episodes": 1,
            "score": 8,
        },
    )

    # Add one more anime to watch list
    await request_watch_add(
        client,
        "kimi-no-na-wa-945779",
        get_test_token,
        {
            "status": "planned",
            "episodes": 0,
            "score": 0,
        },
    )

    # And one more just in case
    await request_watch_add(
        client,
        "kaguya-sama-wa-kokurasetai-ultra-romantic-fcd761",
        get_test_token,
        {
            "status": "completed",
            "episodes": 13,
            "score": 9,
        },
    )

    # Check score asc order
    response = await request_watch_list(
        client, "testuser", {"sort": ["watch_score:asc"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"][0]["score"] == 0
    assert response.json()["list"][1]["score"] == 8
    assert response.json()["list"][2]["score"] == 9

    assert response.json()["list"][0]["anime"]["slug"] == "kimi-no-na-wa-945779"
    assert (
        response.json()["list"][1]["anime"]["slug"] == "bocchi-the-rock-9e172d"
    )
    assert (
        response.json()["list"][2]["anime"]["slug"]
        == "kaguya-sama-wa-kokurasetai-ultra-romantic-fcd761"
    )

    # Check episodes desc order
    response = await request_watch_list(
        client, "testuser", {"sort": ["watch_episodes:desc"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"][0]["episodes"] == 13
    assert response.json()["list"][1]["episodes"] == 1
    assert response.json()["list"][2]["episodes"] == 0

    assert (
        response.json()["list"][0]["anime"]["slug"]
        == "kaguya-sama-wa-kokurasetai-ultra-romantic-fcd761"
    )
    assert (
        response.json()["list"][1]["anime"]["slug"] == "bocchi-the-rock-9e172d"
    )
    assert response.json()["list"][2]["anime"]["slug"] == "kimi-no-na-wa-945779"

    # Check episodes asc order
    response = await request_watch_list(
        client, "testuser", {"sort": ["watch_episodes:asc"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"][0]["episodes"] == 0
    assert response.json()["list"][1]["episodes"] == 1
    assert response.json()["list"][2]["episodes"] == 13

    assert response.json()["list"][0]["anime"]["slug"] == "kimi-no-na-wa-945779"
    assert (
        response.json()["list"][1]["anime"]["slug"] == "bocchi-the-rock-9e172d"
    )
    assert (
        response.json()["list"][2]["anime"]["slug"]
        == "kaguya-sama-wa-kokurasetai-ultra-romantic-fcd761"
    )

    # Check media type desc order
    response = await request_watch_list(
        client, "testuser", {"sort": ["media_type:desc"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"][0]["anime"]["media_type"] == "tv"
    assert response.json()["list"][1]["anime"]["media_type"] == "tv"
    assert response.json()["list"][2]["anime"]["media_type"] == "movie"

    assert (
        response.json()["list"][0]["anime"]["slug"]
        == "kaguya-sama-wa-kokurasetai-ultra-romantic-fcd761"
    )
    assert (
        response.json()["list"][1]["anime"]["slug"] == "bocchi-the-rock-9e172d"
    )
    assert response.json()["list"][2]["anime"]["slug"] == "kimi-no-na-wa-945779"

    # Check media type asc order
    response = await request_watch_list(
        client, "testuser", {"sort": ["media_type:asc"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"][0]["anime"]["media_type"] == "movie"
    assert response.json()["list"][1]["anime"]["media_type"] == "tv"
    assert response.json()["list"][2]["anime"]["media_type"] == "tv"

    assert response.json()["list"][0]["anime"]["slug"] == "kimi-no-na-wa-945779"
    assert (
        response.json()["list"][1]["anime"]["slug"]
        == "kaguya-sama-wa-kokurasetai-ultra-romantic-fcd761"
    )
    assert (
        response.json()["list"][2]["anime"]["slug"] == "bocchi-the-rock-9e172d"
    )
