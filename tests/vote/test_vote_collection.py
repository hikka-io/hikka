from client_requests import request_create_collection
from client_requests import request_vote
from app.models import Collection, Log
from sqlalchemy import select, desc
from app import constants


async def test_vote_collection(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    slugs = [
        "fullmetal-alchemist-brotherhood-fc524a",
        "bocchi-the-rock-9e172d",
        "kaguya-sama-wa-kokurasetai-tensai-tachi-no-renai-zunousen-a3ac07",
        "kaguya-sama-wa-kokurasetai-tensai-tachi-no-renai-zunousen-73a73c",
        "kaguya-sama-wa-kokurasetai-ultra-romantic-fcd761",
        "kimi-no-na-wa-945779",
        "oshi-no-ko-421060",
        "steinsgate-f29797",
    ]

    response = await request_create_collection(
        client,
        get_test_token,
        {
            "tags": [],
            "title": "Test collection",
            "description": "Description",
            "content_type": "anime",
            "visibility": constants.COLLECTION_PUBLIC,
            "labels_order": [],
            "spoiler": False,
            "nsfw": False,
            "content": [
                {
                    "order": index + 1,
                    "comment": None,
                    "label": None,
                    "slug": slug,
                }
                for index, slug in enumerate(slugs)
            ],
        },
    )

    collection_reference = response.json()["reference"]

    collection = await test_session.scalar(
        select(Collection).filter(Collection.id == collection_reference)
    )

    assert collection.vote_score == 0

    await request_vote(
        client,
        get_test_token,
        constants.CONTENT_COLLECTION,
        collection_reference,
        1,
    )

    await test_session.refresh(collection)
    assert collection.vote_score == 1

    # Before we move on let's check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_VOTE_SET
    assert log.user == create_test_user

    assert log.data["content_type"] == constants.CONTENT_COLLECTION
    assert log.data["user_score"] == 1
    assert log.data["old_score"] == 0
    assert log.data["new_score"] == 1
