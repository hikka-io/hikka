from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response

async def request_admin_update_user(
        client: TestClient, token: str, username: str,
        forbid_actions: list[str] | None = None,
        forbid_actions_merge: bool = False,
        remove_avatar: bool = False,
        remove_cover: bool = False,
        description: str | None = None,
        remove_description: bool = False,
        banned: bool | None = None,
) -> Response:
    return await client.patch(
        f"/admin/user/{username}",
        json={
            "forbid_actions": forbid_actions,
            "forbid_actions_merge": forbid_actions_merge,
            "remove_avatar": remove_avatar,
            "remove_cover": remove_cover,
            "description": description,
            "remove_description": remove_description,
            "banned": banned,
        },
        headers={"Auth": token},
    )
