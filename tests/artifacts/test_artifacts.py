from client_requests import request_artifact_privacy
from client_requests import request_artifact
from app.models import Artifact
from app.utils import utcnow
from fastapi import status


async def test_artifacts(
    client,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    now = utcnow()
    artifact = Artifact(
        **{
            "user_id": create_test_user.id,
            "data": {"hello": "there"},
            "created": now,
            "updated": now,
            "name": "test",
        }
    )

    test_session.add(artifact)
    await test_session.commit()

    response = await request_artifact(
        client,
        create_test_user.username,
        "test",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = await request_artifact(
        client, create_test_user.username, "test", get_dummy_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = await request_artifact(
        client, create_test_user.username, "test", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK

    # Setting artifat to be public
    await request_artifact_privacy(client, "test", False, get_test_token)

    response = await request_artifact(
        client,
        create_test_user.username,
        "test",
    )

    assert response.status_code == status.HTTP_200_OK

    response = await request_artifact(
        client, create_test_user.username, "test", get_dummy_token
    )

    assert response.status_code == status.HTTP_200_OK

    response = await request_artifact(
        client, create_test_user.username, "test", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
