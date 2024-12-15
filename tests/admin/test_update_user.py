from app import constants
from tests.client_requests import (
    request_admin_update_user,
    request_client_create,
)


async def test_nothing_to_update(client, test_user, token_admin):
    response = await request_admin_update_user(
        client, token_admin, test_user.username
    )
    assert response.status_code == 400
    assert response.json()["code"] == "admin:nothing_to_update"


async def test_forbid_action(client, test_user, test_token, token_admin):
    forbid_actions = [constants.PERMISSION_CLIENT_CREATE]
    response = await request_admin_update_user(
        client, token_admin, test_user.username, forbid_actions
    )

    assert response.status_code == 200

    response = await request_client_create(
        client, test_token, "test-client", "test-client", "http://localhost"
    )

    assert response.status_code == 403


async def test_forbid_action_merge(
    client, test_user, test_token, token_admin, test_session
):
    # Ensure user has forbidden actions to merge
    test_user.forbidden_actions = [constants.PERMISSION_CLIENT_UPDATE]
    await test_session.commit()

    forbid_actions = [constants.PERMISSION_CLIENT_CREATE]
    response = await request_admin_update_user(
        client,
        token_admin,
        test_user.username,
        forbid_actions,
        forbid_actions_merge=True,
    )

    assert response.status_code == 200

    await test_session.refresh(test_user)

    # Sets are checked regardless of order
    assert set(test_user.forbidden_actions) == {
        constants.PERMISSION_CLIENT_UPDATE,
        constants.PERMISSION_CLIENT_CREATE,
    }


async def test_remove_description(client, test_user, token_admin, test_session):
    # Ensure user have description
    test_user.description = "Test description"
    await test_session.commit()

    response = await request_admin_update_user(
        client, token_admin, test_user.username, remove_description=True
    )

    assert response.status_code == 200

    await test_session.refresh(test_user)

    assert test_user.description is None


async def test_ban(client, test_user, token_admin, test_session):
    # Ensure user have not been banned
    test_user.banned = False
    await test_session.commit()
    response = await request_admin_update_user(
        client, token_admin, test_user.username, banned=True
    )

    assert response.status_code == 200

    await test_session.refresh(test_user)

    assert test_user.banned is True
