from client_requests import request_favourite_delete
from client_requests import request_favourite_list
from client_requests import request_favourite_add
from client_requests import request_favourite
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_favourite_person_add(
    client,
    create_test_user,
    aggregator_people,
    get_test_token,
    test_session,
):
    # Person should not be in favourite when we start
    response = await request_favourite(
        client, "person", "makoto-shinkai-943611", get_test_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "favourite:not_found"

    # Add person to favourite
    response = await request_favourite_add(
        client, "person", "makoto-shinkai-943611", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK

    # Add person to favourite one more time to get an error
    response = await request_favourite_add(
        client, "person", "makoto-shinkai-943611", get_test_token
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "favourite:exists"

    # Now person should be in favourite
    response = await request_favourite(
        client, "person", "makoto-shinkai-943611", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK

    # Check person favourite log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_FAVOURITE
    assert log.user == create_test_user
    assert log.data == {"content_type": "person"}


async def test_favourite_person_add_bad_slug(
    client,
    create_test_user,
    aggregator_people,
    get_test_token,
):
    # Try to add non existing person to favourite
    response = await request_favourite_add(
        client, "person", "bad-person", get_test_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "favourite:content_not_found"


async def test_favourite_person_delete(
    client,
    create_test_user,
    aggregator_people,
    get_test_token,
    test_session,
):
    # Add person to favourite
    await request_favourite_add(
        client, "person", "makoto-shinkai-943611", get_test_token
    )

    # Now delete it
    response = await request_favourite_delete(
        client, "person", "makoto-shinkai-943611", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True

    # Person should be gone from favourite
    response = await request_favourite(
        client, "person", "makoto-shinkai-943611", get_test_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Check person favourite remove log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_FAVOURITE_REMOVE
    assert log.data == {"content_type": "person"}


async def test_favourite_person_list(
    client,
    create_test_user,
    aggregator_people,
    get_test_token,
):
    # User favourite list should be empty when we start
    response = await request_favourite_list(client, "person", "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 0

    # Add person to favourite
    await request_favourite_add(
        client, "person", "makoto-shinkai-943611", get_test_token
    )

    # Now let's check again
    response = await request_favourite_list(client, "person", "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["slug"] == "makoto-shinkai-943611"
    assert response.json()["list"][0]["data_type"] == "person"
    assert response.json()["list"][0]["favourite_created"] is not None

    # Add one more person to favourite
    await request_favourite_add(
        client, "person", "yasuhiro-irie-5b4e11", get_test_token
    )

    # Newest favourite should go first
    response = await request_favourite_list(client, "person", "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2
    assert len(response.json()["list"]) == 2
    assert response.json()["list"][0]["slug"] == "yasuhiro-irie-5b4e11"
    assert response.json()["list"][1]["slug"] == "makoto-shinkai-943611"
