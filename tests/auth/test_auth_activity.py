from sqlalchemy.ext.asyncio import AsyncSession
from client_requests import request_watch_add
from client_requests import request_watch
from client_requests import request_me
from app.models import AuthToken, User
from datetime import timedelta
from app.utils import utcnow
from sqlalchemy import select
from fastapi import status


async def get_token(test_session, secret):
    return await test_session.scalar(
        select(AuthToken)
        .filter(AuthToken.secret == secret)
        .execution_options(populate_existing=True)
    )


async def get_user(test_session, user_id):
    return await test_session.scalar(
        select(User)
        .filter(User.id == user_id)
        .execution_options(populate_existing=True)
    )


async def test_auth_activity(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
    monkeypatch,
):
    slug = "bocchi-the-rock-9e172d"

    response = await request_watch_add(
        client, slug, get_test_token, {"status": "watching"}
    )

    assert response.status_code == status.HTTP_200_OK

    commits = []
    commit = AsyncSession.commit

    async def tracked_commit(self):
        commits.append(self)
        return await commit(self)

    monkeypatch.setattr(AsyncSession, "commit", tracked_commit)

    # Token, activity and expiration are fresh so auth has nothing to save
    for request in [
        lambda: request_me(client, get_test_token),
        # Two auth dependencies with anime query between them
        lambda: request_watch(client, slug, get_test_token),
    ]:
        response = await request()

        assert response.status_code == status.HTTP_200_OK
        assert commits == []

    # Stale values get saved again
    token = await get_token(test_session, get_test_token)
    user = await get_user(test_session, token.user_id)

    stale = utcnow() - timedelta(minutes=10)
    token.expiration = utcnow() + timedelta(days=1)
    user.last_active = stale
    token.used = stale

    await test_session.commit()
    commits.clear()

    response = await request_watch(client, slug, get_test_token)

    assert response.status_code == status.HTTP_200_OK

    # One commit for token use and one for activity and expiration
    assert len(commits) == 2

    token = await get_token(test_session, get_test_token)
    user = await get_user(test_session, token.user_id)

    assert token.used > stale
    assert user.last_active > stale
    assert token.expiration > utcnow() + timedelta(days=29)

    # Next request finds everything fresh again
    commits.clear()

    response = await request_watch(client, slug, get_test_token)

    assert response.status_code == status.HTTP_200_OK
    assert commits == []
