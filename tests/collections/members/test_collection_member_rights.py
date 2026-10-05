from client_requests import request_create_collection
from client_requests import request_update_collection
from client_requests import request_delete_collection
from client_requests import request_collections
from fastapi import status
from app import constants
import helpers


# Two entries under two labels, so a co-author can reorder them
RIGHTS_CONTENT = [
    {
        "slug": "fullmetal-alchemist-brotherhood-fc524a",
        "comment": None,
        "label": "Good",
        "order": 1,
    },
    {
        "slug": "bocchi-the-rock-9e172d",
        "comment": "Author comment",
        "label": "Great",
        "order": 2,
    },
]


def collection_args(**kwargs):
    return helpers.collection_args(
        **{
            "labels_order": ["Good", "Great"],
            "content": RIGHTS_CONTENT,
            **kwargs,
        }
    )


async def add_editor(test_session, reference, user):
    member = helpers.make_collection_member(user, collection_id=reference)

    test_session.add(member)
    await test_session.commit()

    return member


async def test_collection_editor_full_edit(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    response = await request_create_collection(
        client, get_test_token, collection_args()
    )

    assert response.status_code == status.HTTP_200_OK

    reference = response.json()["reference"]
    await add_editor(test_session, reference, create_dummy_user)

    # Co-author must get the full edit path, not the restricted moderator
    # one: content and labels_order included
    response = await request_update_collection(
        client,
        reference,
        get_dummy_token,
        collection_args(
            title="Edited by co-author",
            labels_order=["Great", "Good"],
            content=[
                {
                    "slug": "bocchi-the-rock-9e172d",
                    "comment": None,
                    "label": "Great",
                    "order": 1,
                },
                {
                    "slug": "fullmetal-alchemist-brotherhood-fc524a",
                    "comment": "Co-author comment",
                    "label": "Good",
                    "order": 2,
                },
            ],
        ),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Edited by co-author"
    assert response.json()["labels_order"] == ["Great", "Good"]
    assert response.json()["my_role"] == constants.COLLECTION_MEMBER_EDITOR

    # Content really changed, so the co-author did not land on the
    # restricted moderator path
    assert (
        response.json()["collection"][0]["content"]["slug"]
        == "bocchi-the-rock-9e172d"
    )
    assert response.json()["collection"][1]["comment"] == "Co-author comment"


async def test_collection_editor_cant_change_visibility(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    response = await request_create_collection(
        client, get_test_token, collection_args()
    )

    reference = response.json()["reference"]
    await add_editor(test_session, reference, create_dummy_user)

    response = await request_update_collection(
        client,
        reference,
        get_dummy_token,
        collection_args(visibility=constants.COLLECTION_UNLISTED),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "collections:visibility_owner_only"


async def test_collection_editor_cant_delete(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    response = await request_create_collection(
        client, get_test_token, collection_args()
    )

    reference = response.json()["reference"]
    await add_editor(test_session, reference, create_dummy_user)

    response = await request_delete_collection(
        client, reference, get_dummy_token
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"


async def test_collection_list_includes_co_authored(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    response = await request_create_collection(
        client, get_test_token, collection_args()
    )

    reference = response.json()["reference"]
    await add_editor(test_session, reference, create_dummy_user)

    # The author filter is membership based now, so the collection shows up
    # on the co-author's profile even though author_id points elsewhere
    response = await request_collections(
        client, filters={"author": "dummy"}, token=get_dummy_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["reference"] == reference

    # And author_id still credits the creator
    assert response.json()["list"][0]["author"]["username"] == "testuser"
