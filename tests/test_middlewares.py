from app.middlewares import register_profiling_middleware
from async_asgi_testclient import TestClient
from fastapi import FastAPI, status
from types import SimpleNamespace
from unittest import mock
from pathlib import Path


async def test_profiling_path_outside(tmp_path):
    settings = SimpleNamespace(
        profiling=SimpleNamespace(
            enabled=True,
            trigger="all",
            path=str(tmp_path / "profiles"),
            profiling_secret="secret",
        )
    )

    calls = []
    test_app = FastAPI()

    @test_app.get("/{path:path}")
    async def catch_all(path: str):
        calls.append(path)
        return {"path": path}

    with mock.patch("app.middlewares.get_settings", return_value=settings):
        register_profiling_middleware(test_app)

    async with TestClient(test_app) as client:
        # Regular request is profiled
        response = await client.get("/anime/test")
        assert response.status_code == status.HTTP_200_OK
        assert calls == ["anime/test"]

        # Path leading outside of profiles directory still runs only once
        calls.clear()
        response = await client.get("/a/../../escape")
        assert response.status_code == status.HTTP_200_OK
        assert calls == ["a/../../escape"]

    # Only regular request left its profile
    profiles = [
        profile.relative_to(tmp_path) for profile in tmp_path.rglob("*.html")
    ]

    assert [profile.parent for profile in profiles] == [
        Path("profiles/anime/test")
    ]
