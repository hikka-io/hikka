# Based on https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html
# https://github.com/gpkc/fastapi-sqlalchemy-pytest

from pytest_postgresql.janitor import DatabaseJanitor
from app.database import sessionmanager, get_session
from app.models import Anime, Manga, Novel, Base
from async_asgi_testclient import TestClient
from pytest_postgresql import factories
from sqlalchemy.orm import selectinload
from sqlalchemy import select, text
from app.utils import get_settings
from contextlib import ExitStack
from sqlalchemy import make_url
from datetime import datetime
from app import aggregator
from app import create_app
from app import constants
from unittest import mock
import asyncio
import helpers
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
async def test_user(test_session):
    return await helpers.create_user(test_session)


@pytest.fixture
async def create_test_user(test_user):
    return test_user


@pytest.fixture
async def create_test_user_oauth(test_session):
    return await helpers.create_user(test_session, email="testuser@mail.com")


@pytest.fixture
async def moderator_user(test_session):
    return await helpers.create_user(
        test_session,
        username="moderator",
        email="moderator@mail.com",
        role=constants.ROLE_MODERATOR,
    )


@pytest.fixture
async def moderator_token(test_session, moderator_user):
    return (
        await helpers.create_token(
            test_session, moderator_user.email, "moderator-token"
        )
    ).secret


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
async def create_dummy_user_restricted(test_session):
    return await helpers.create_user(
        test_session,
        username="dummy",
        email="dummy@mail.com",
        role=constants.ROLE_RESTRICTED,
    )


@pytest.fixture
async def create_test_user_not_activated(test_session):
    return await helpers.create_user(test_session, activated=False)


@pytest.fixture
async def create_test_user_with_oauth(test_session):
    user = await helpers.create_user(test_session)
    return await helpers.create_oauth(test_session, user.id)


@pytest.fixture
async def test_token(test_user, test_session):
    token = await helpers.create_token(
        test_session, test_user.email, "SECRET_TOKEN"
    )

    return token.secret


@pytest.fixture
async def get_test_token(test_token):
    return test_token


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


# Fix utcnow() datetime for tests that rely on it not changing within the duration of the test
# https://docs.pytest.org/en/stable/how-to/monkeypatch.html
@pytest.fixture(autouse=False)
def mock_utcnow(monkeypatch):
    fixed_time = datetime(2024, 2, 17, 10, 23, 29, 305502)

    # When a function is imported, it becomes a part of the namespace of the
    # module that imported it. We need to patch the specific function reference
    # in the module we're testing
    monkeypatch.setattr("app.edit.service.utcnow", lambda: fixed_time)
    monkeypatch.setattr("app.comments.service.utcnow", lambda: fixed_time)


# Aggregator fixtures
@pytest.fixture
async def aggregator_genres(test_session):
    data = await helpers.load_json("tests/data/anime_genres.json")

    await aggregator.save_genres(test_session, data)


@pytest.fixture
async def aggregator_anime_roles(test_session):
    data = await helpers.load_json("tests/data/anime_roles.json")

    await aggregator.update_anime_roles(test_session, data)

    await aggregator.update_anime_role_weights(test_session)


@pytest.fixture
async def aggregator_manga_roles(test_session):
    data = await helpers.load_json("tests/data/manga_roles.json")

    await aggregator.update_manga_roles(test_session, data)


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
async def aggregator_manga(test_session):
    data = await helpers.load_json("tests/data/manga.json")

    await aggregator.save_manga_list(test_session, data["list"])


@pytest.fixture
async def aggregator_novel(test_session):
    data = await helpers.load_json("tests/data/novels.json")

    await aggregator.save_novel_list(test_session, data["list"])


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
async def aggregator_manga_info(test_session):
    manga_list = {
        "fb9fbd44-76f6-4b22-9438-05d7e3a43c37": "berserk.json",
        "7ef8d2cf-0565-4ddd-9498-7fae392a7421": "fma.json",
        "f9ebc0e1-7c08-499d-8c0e-7e531683c4aa": "horizon.json",
        "7cc791e6-392a-4560-8809-ae2a9cad205b": "heaven.json",
    }

    for slug in manga_list:
        if manga := await test_session.scalar(
            select(Manga)
            .filter(Manga.content_id == slug)
            .options(selectinload(Manga.genres))
        ):
            data = await helpers.load_json(
                f"tests/data/manga_info/{manga_list[slug]}"
            )

            await aggregator.update_manga_info(
                test_session,
                manga,
                data,
            )


@pytest.fixture
async def aggregator_novel_info(test_session):
    novel_list = {
        "7bb1594b-9a84-4632-948d-594903e85676": "tian.json",
        "cc552518-5e42-43fa-a729-0f9a81db5767": "konosuba.json",
    }

    for slug in novel_list:
        if novel := await test_session.scalar(
            select(Novel)
            .filter(Novel.content_id == slug)
            .options(selectinload(Novel.genres))
        ):
            data = await helpers.load_json(
                f"tests/data/novel_info/{novel_list[slug]}"
            )

            await aggregator.update_novel_info(
                test_session,
                novel,
                data,
            )


@pytest.fixture
async def aggregator_anime_franchises(test_session):
    data = await helpers.load_json("tests/data/anime_franchises.json")

    await aggregator.save_franchises_list(test_session, data["list"])


@pytest.fixture
async def test_thirdparty_client(test_session, test_user):
    return await helpers.create_client(
        test_session, test_user, "test-thirdparty-client"
    )


@pytest.fixture
async def test_thirdparty_token(
    test_session, test_user, test_thirdparty_client
):
    return (
        await helpers.create_token(
            test_session,
            test_user.email,
            "thirdparty-token-secret",
            test_thirdparty_client,
        )
    ).secret
