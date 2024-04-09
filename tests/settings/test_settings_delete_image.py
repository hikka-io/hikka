from client_requests import request_settings_delete_image
from client_requests import request_upload
from client_requests import request_me
from sqlalchemy import select, desc
from app.models import Log
from app import constants


async def test_settings_delete_avatar(
    client,
    create_test_user,
    get_test_token,
    test_session,
    mock_s3_upload_file,
):
    # First let's upload test image
    with open("tests/data/upload/test.jpg", mode="rb") as file:
        await request_upload(client, "avatar", get_test_token, file)

    # Than make sure user has uploaded avatar
    response = await request_me(client, get_test_token)
    assert response.json()["avatar"] != "https://cdn.hikka.io/avatar.jpg"

    # Now delete avatar
    await request_settings_delete_image(client, get_test_token, "avatar")

    # And check it again
    response = await request_me(client, get_test_token)
    assert response.json()["avatar"] == "https://cdn.hikka.io/avatar.jpg"

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_SETTINGS_IMAGE_DELETE
    assert log.user == create_test_user
    assert log.data["image_type"] == "avatar"
    assert "image_id" in log.data


async def test_settings_delete_cover(
    client,
    create_test_user,
    get_test_token,
    test_session,
    mock_s3_upload_file,
):
    # First let's upload test image
    with open("tests/data/upload/cover.jpg", mode="rb") as file:
        await request_upload(client, "cover", get_test_token, file)

    # Than make sure user has uploaded cover
    response = await request_me(client, get_test_token)
    assert response.json()["cover"] is not None

    # Now delete cover
    await request_settings_delete_image(client, get_test_token, "cover")

    # And check it again
    response = await request_me(client, get_test_token)
    assert response.json()["cover"] is None

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_SETTINGS_IMAGE_DELETE
    assert log.user == create_test_user
    assert log.data["image_type"] == "cover"
    assert "image_id" in log.data
