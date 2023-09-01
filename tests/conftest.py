# Based on https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html
# https://github.com/gpkc/fastapi-sqlalchemy-pytest

from pytest_postgresql.janitor import DatabaseJanitor
from app.database import sessionmanager, get_session
from app.auth.oauth_client import OAuthError
from async_asgi_testclient import TestClient
from datetime import datetime, timedelta
from pytest_postgresql import factories
from sqlalchemy.orm import selectinload
from app.settings import get_settings
from contextlib import ExitStack
from sqlalchemy import make_url
from sqlalchemy import select
from httpx import Response
from app import create_app
from app import aggregator
from unittest import mock
import helpers
import asyncio
import pytest


from app.models import (
    AuthToken,
    Anime,
    User,
    Base,
)

# This is needed to obtain PostgreSQL version
test_db = factories.postgresql_proc()


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield create_app(init_db=False)


@pytest.fixture
async def client(app):
    async with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def connection_test(test_db, event_loop):
    # Switch to testing config using env variable
    settings = get_settings()
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")

    db_url = make_url(settings.database.endpoint)

    pg_password = db_url.password
    pg_user = db_url.username
    pg_db = db_url.database
    pg_host = db_url.host
    pg_port = db_url.port

    with DatabaseJanitor(
        pg_user, pg_host, pg_port, pg_db, test_db.version, pg_password
    ):
        sessionmanager.init(settings.database.endpoint)
        yield
        await sessionmanager.close()


@pytest.fixture(scope="function", autouse=True)
async def create_tables(connection_test):
    async with sessionmanager.connect() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="function", autouse=True)
async def session_override(app, connection_test):
    async def get_session_override():
        async with sessionmanager.session() as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override


@pytest.fixture
async def test_session():
    async with sessionmanager.session() as session:
        yield session


@pytest.fixture
async def create_test_user(test_session):
    await helpers.create_user(test_session)


@pytest.fixture
async def create_dummy_user(test_session):
    await helpers.create_user(
        test_session, username="dummy", email="dummy@mail.com"
    )


@pytest.fixture
async def create_test_user_not_activated(test_session):
    await helpers.create_user(test_session, activated=False)


@pytest.fixture
async def create_test_user_with_oauth(test_session):
    user = await helpers.create_user(test_session)
    await helpers.create_oauth(test_session, user.id)


@pytest.fixture
async def get_test_token(test_session):
    now = datetime.utcnow()

    user = await test_session.scalar(
        select(User).filter(User.email == "user@mail.com")
    )

    token = AuthToken(
        **{
            "expiration": now + timedelta(minutes=30),
            "secret": "SECRET_TOKEN",
            "created": now,
            "user": user,
        }
    )

    test_session.add(token)
    await test_session.commit()

    return token.secret


# OAuth fixtures
@pytest.fixture(autouse=True)
def oauth_response():
    def generate(status_code=200, **params):
        return Response(status_code, **params)

    return generate


@pytest.fixture(autouse=False)
def oauth_http(oauth_response):
    with mock.patch("httpx.AsyncClient.request") as mocked:
        mocked.return_value = oauth_response(
            json={
                "email": "user@mail.com",
                "response": "ok",
                "id": "test-id",
            }
        )

        yield mocked


@pytest.fixture(autouse=False)
def oauth_fail_http(oauth_response):
    with mock.patch(
        "httpx.AsyncClient.request", side_effect=OAuthError
    ) as mocked:
        yield mocked


# Aggregator fixtures
@pytest.fixture
async def aggregator_anime_genres(test_session):
    data = await helpers.load_json("tests/aggregator/data/anime_genres.json")

    await aggregator.save_anime_genres(test_session, data)


@pytest.fixture
async def aggregator_anime_roles(test_session):
    data = await helpers.load_json("tests/aggregator/data/anime_roles.json")

    await aggregator.update_anime_roles(test_session, data)


@pytest.fixture
async def aggregator_characters(test_session):
    data = await helpers.load_json("tests/aggregator/data/characters.json")

    await aggregator.save_characters(test_session, data["list"])


@pytest.fixture
async def aggregator_people(test_session):
    data = await helpers.load_json("tests/aggregator/data/people.json")

    await aggregator.save_people(test_session, data["list"])


@pytest.fixture
async def aggregator_anime(test_session):
    data = await helpers.load_json("tests/aggregator/data/anime.json")

    await aggregator.save_anime_list(test_session, data["list"])


@pytest.fixture
async def aggregator_anime_info(test_session):
    anime_list = {
        "fc524a18-378f-4ccb-82a0-b4063206c600": "fma.json",
        "f297970c-93e7-47f0-a01d-ee4cd1f067d9": "steins_gate.json",
        "a3ac0776-67f6-474b-83ba-7df7a3c2e3f6": "kaguya_1.json",
        "73a73ca9-fcea-4521-ad88-fa5206ad8e78": "kaguya_2.json",
        "fcd76158-66b6-4c72-8c1c-5aa801a5efff": "kaguya_3.json",
    }

    for slug in anime_list:
        if anime := await test_session.scalar(
            select(Anime)
            .filter(Anime.content_id == slug)
            .options(selectinload(Anime.genres))
        ):
            data = await helpers.load_json(
                f"tests/aggregator/data/anime_info/{anime_list[slug]}"
            )

            await aggregator.update_anime_info(
                test_session,
                anime,
                data,
            )


@pytest.fixture
async def aggregator_anime_franchises(test_session):
    data = await helpers.load_json(
        "tests/aggregator/data/anime_franchises.json"
    )

    await aggregator.save_anime_franchises_list(test_session, data["list"])
