# Based on https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html
# https://github.com/gpkc/fastapi-sqlalchemy-pytest

from pytest_postgresql.janitor import DatabaseJanitor
from app.database import sessionmanager, get_session
from async_asgi_testclient import TestClient
from datetime import datetime, timedelta
from pytest_postgresql import factories
from app.settings import get_settings
from app.auth.utils import hashpwd
from contextlib import ExitStack
from sqlalchemy import make_url
from sqlalchemy import select
from app import create_app
import asyncio
import pytest

from app.models import (
    AuthToken,
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
    now = datetime.utcnow()

    user = User(
        **{
            "password_hash": hashpwd("password"),
            "email": "user@mail.com",
            "username": "username",
            "last_active": now,
            "activated": True,
            "created": now,
            "login": now,
        }
    )

    test_session.add(user)
    await test_session.commit()


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
