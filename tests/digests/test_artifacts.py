from client_requests import request_digest_privacy
from client_requests import request_digest
from app.models import Digest
from app.utils import utcnow
from fastapi import status


async def test_digests(
    client,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    now = utcnow()
    digest = Digest(
        **{
            "user_id": create_test_user.id,
            "data": {"hello": "there"},
            "created": now,
            "updated": now,
            "name": "test",
        }
    )

    test_session.add(digest)
    await test_session.commit()

    response = await request_digest(
        client,
        create_test_user.username,
        "test",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = await request_digest(
        client, create_test_user.username, "test", get_dummy_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = await request_digest(
        client, create_test_user.username, "test", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK

    # Setting artifat to be public
    await request_digest_privacy(client, "test", False, get_test_token)

    response = await request_digest(
        client,
        create_test_user.username,
        "test",
    )

    assert response.status_code == status.HTTP_200_OK

    response = await request_digest(
        client, create_test_user.username, "test", get_dummy_token
    )

    assert response.status_code == status.HTTP_200_OK

    response = await request_digest(
        client, create_test_user.username, "test", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
