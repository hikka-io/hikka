# Based on https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html
# https://github.com/gpkc/fastapi-sqlalchemy-pytest

from pytest_postgresql.janitor import DatabaseJanitor
from app.database import sessionmanager, get_session
from async_asgi_testclient import TestClient
from pytest_postgresql import factories
from sqlalchemy.orm import selectinload
from sqlalchemy import select, text
from app.utils import get_settings
from app.models import Anime, Base
from contextlib import ExitStack
from sqlalchemy import make_url
from app import create_app
from app import aggregator
from unittest import mock
from app import constants
import helpers
import asyncio
import pytest


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
        await connection.execute(text("CREATE EXTENSION IF NOT EXISTS ltree;"))
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
    return await helpers.create_user(test_session)


@pytest.fixture
async def create_test_user_oauth(test_session):
    return await helpers.create_user(test_session, email="testuser@mail.com")


@pytest.fixture
async def create_test_user_moderator(test_session):
    return await helpers.create_user(
        test_session,
        role=constants.ROLE_MODERATOR,
    )


@pytest.fixture
async def create_dummy_user(test_session):
    return await helpers.create_user(
        test_session, username="dummy", email="dummy@mail.com"
    )


@pytest.fixture
async def create_dummy_user_banned(test_session):
    return await helpers.create_user(
        test_session,
        username="dummy",
        email="dummy@mail.com",
        role=constants.ROLE_BANNED,
    )


@pytest.fixture
async def create_test_user_not_activated(test_session):
    return await helpers.create_user(test_session, activated=False)


@pytest.fixture
async def create_test_user_with_oauth(test_session):
    user = await helpers.create_user(test_session)
    return await helpers.create_oauth(test_session, user.id)


@pytest.fixture
async def get_test_token(test_session):
    token = await helpers.create_token(
        test_session, "user@mail.com", "SECRET_TOKEN"
    )

    return token.secret


@pytest.fixture
async def get_dummy_token(test_session):
    token = await helpers.create_token(
        test_session, "dummy@mail.com", "DUMMY_TOKEN"
    )

    return token.secret


# OAuth fixtures
@pytest.fixture(autouse=False)
def mock_oauth_data():
    with mock.patch("app.auth.oauth.get_user_data") as mocked:
        mocked.return_value = {
            "email": "testuser@mail.com",
            "id": "TEST_OAUTH_ID",
        }

        yield mocked


@pytest.fixture(autouse=False)
def mock_oauth_invalid_data():
    with mock.patch("app.upload.service.s3_upload_file") as mocked:
        mocked.return_value = None
        yield mocked


# S3 fixtures
@pytest.fixture(autouse=False)
def mock_s3_upload_file():
    with mock.patch("app.upload.service.s3_upload_file") as mocked:
        mocked.return_value = True
        yield mocked


# Aggregator fixtures
@pytest.fixture
async def aggregator_anime_genres(test_session):
    data = await helpers.load_json("tests/data/anime_genres.json")

    await aggregator.save_anime_genres(test_session, data)


@pytest.fixture
async def aggregator_anime_roles(test_session):
    data = await helpers.load_json("tests/data/anime_roles.json")

    await aggregator.update_anime_roles(test_session, data)

    await aggregator.update_anime_role_weights(test_session)


@pytest.fixture
async def aggregator_characters(test_session):
    data = await helpers.load_json("tests/data/characters.json")

    await aggregator.save_characters(test_session, data["list"])


@pytest.fixture
async def aggregator_people(test_session):
    data = await helpers.load_json("tests/data/people.json")

    await aggregator.save_people(test_session, data["list"])


@pytest.fixture
async def aggregator_companies(test_session):
    data = await helpers.load_json("tests/data/companies.json")

    await aggregator.save_companies(test_session, data["list"])


@pytest.fixture
async def aggregator_anime(test_session):
    data = await helpers.load_json("tests/data/anime.json")

    await aggregator.save_anime_list(test_session, data["list"])


@pytest.fixture
async def aggregator_anime_info(test_session):
    anime_list = {
        "fc524a18-378f-4ccb-82a0-b4063206c600": "fma.json",
        "f297970c-93e7-47f0-a01d-ee4cd1f067d9": "steins_gate.json",
        "a3ac0776-67f6-474b-83ba-7df7a3c2e3f6": "kaguya_1.json",
        "73a73ca9-fcea-4521-ad88-fa5206ad8e78": "kaguya_2.json",
        "fcd76158-66b6-4c72-8c1c-5aa801a5efff": "kaguya_3.json",
        "0cf69ac6-9238-4e2f-9add-39294c1a0f11": "snk_1.json",
        "b88bf4b4-564e-43d4-8f1a-01741d244366": "snk_2.json",
        "b22bb359-4545-45ce-92d3-df8646554128": "snk_3_1.json",
        "91a35018-3439-47b1-8eb8-ba2092fd0191": "snk_3_2.json",
        "4877caaf-d76d-46f2-9a73-cbdb2fef202b": "snk_4_1.json",
        "8d3fc3a7-1fa5-4ce4-909f-3d60ca2d072e": "snk_4_2.json",
        "833be1cc-b3ef-4ebc-8017-07f49203a8a0": "snk_4_3.json",
        "94577949-789f-4c5c-bb56-a88b243254bb": "name.json",
        "9e172d54-b1a8-4aef-a396-67f6dddbfb07": "bocchi.json",
        "4210609f-9fcb-448b-b871-adbd06e1faf8": "oshi.json",
        "227414cb-51df-43e8-b82e-49871b372054": "carrot.json",
        "167704d8-28fd-4f8a-aab2-1e9cabb30b20": "euphoria.json",
    }

    for slug in anime_list:
        if anime := await test_session.scalar(
            select(Anime)
            .filter(Anime.content_id == slug)
            .options(selectinload(Anime.genres))
        ):
            data = await helpers.load_json(
                f"tests/data/anime_info/{anime_list[slug]}"
            )

            await aggregator.update_anime_info(
                test_session,
                anime,
                data,
            )

    await aggregator.update_anime_staff_weights(test_session)


@pytest.fixture
async def aggregator_anime_franchises(test_session):
    data = await helpers.load_json("tests/data/anime_franchises.json")

    await aggregator.save_anime_franchises_list(test_session, data["list"])
