from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import sessionmanager
import fastapi.openapi.utils as fu
from .settings import get_settings
from fastapi import FastAPI
from . import errors


def create_app(init_db: bool = True) -> FastAPI:
    settings = get_settings()
    lifespan = None

    # SQLAlchemy initialization process
    if init_db:
        sessionmanager.init(settings.database.endpoint)

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield
            if sessionmanager._engine is not None:
                await sessionmanager.close()

    fu.validation_error_response_definition = (
        errors.ErrorResponse.model_json_schema()
    )

    app = FastAPI(
        title="Hikka API",
        version="0.1.5",
        openapi_tags=[
            {"name": "Auth"},
            {"name": "User"},
            {"name": "Follow"},
            {"name": "Anime"},
            {"name": "Characters"},
            {"name": "Companies"},
            {"name": "People"},
            {"name": "Favourite"},
            {"name": "Watch"},
            {"name": "Edit"},
        ],
        lifespan=lifespan,
        # redoc_url=None,
        # docs_url=None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(errors.Abort, errors.abort_handler)
    app.add_exception_handler(
        RequestValidationError,
        errors.validation_handler,
    )

    from .characters import router as characters_router
    from .companies import router as companies_router
    from .favourite import router as favourite_router
    from .people import router as people_router
    from .follow import router as follow_router
    from .anime import router as anime_router
    from .watch import router as watch_router
    from .user import router as user_router
    from .auth import router as auth_router
    from .edit import router as edit_router

    app.include_router(characters_router)
    app.include_router(companies_router)
    app.include_router(favourite_router)
    app.include_router(people_router)
    app.include_router(follow_router)
    app.include_router(anime_router)
    app.include_router(watch_router)
    app.include_router(user_router)
    app.include_router(auth_router)
    app.include_router(edit_router)

    @app.get("/ping")
    async def ping_pong():
        return "pong"

    return app
