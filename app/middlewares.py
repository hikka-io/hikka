from pyinstrument.renderers.html import HTMLRenderer
from fastapi import FastAPI, Request
from app.utils import get_settings
from pyinstrument import Profiler
from datetime import datetime
from typing import Callable
from pathlib import Path


# https://blog.balthazar-rouberol.com/how-to-profile-a-fastapi-asynchronous-request
def register_profiling_middleware(app: FastAPI):
    settings = get_settings()

    if not settings.profiling.enabled:
        return

    if settings.profiling.trigger not in ["query", "all"]:
        return

    @app.middleware("http")
    async def profile_request(request: Request, call_next: Callable):
        """
        Profile the current request
        Taken from https://pyinstrument.readthedocs.io/en/latest/guide.html#profile-a-web-request-in-fastapi
        with small improvements.
        """

        if (
            settings.profiling.trigger == "all"
            or settings.profiling.trigger == "query"
            and request.query_params.get("profiling_flag", False)
            and request.query_params.get("profiling_secret", None) == settings.profiling.profiling_secret
        ):
            with Profiler(interval=0.001, async_mode="enabled") as profiler:
                response = await call_next(request)

            path = f"{settings.profiling.path}/{request.url.path}"
            path = path.replace("//", "/")
            Path(path).mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

            with open(f"{path}/{timestamp}_profile.html", "w") as out:
                out.write(profiler.output(renderer=HTMLRenderer()))

            return response

        # Proceed without profiling
        return await call_next(request)
