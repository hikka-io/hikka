from prometheus_fastapi_instrumentator import Instrumentator
from app.middlewares import register_profiling_middleware
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import sessionmanager
from app.utils import TimeoutMiddleware
from app.utils import get_settings
import fastapi.openapi.utils as fu
from fastapi import FastAPI
from app import errors


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
        version="0.4.2",
        openapi_tags=[
            {"name": "Admin"},
            {"name": "Auth"},
            {"name": "Client"},
            {"name": "User"},
            {"name": "Follow"},
            {"name": "Anime"},
            {"name": "Manga"},
            {"name": "Novel"},
            {"name": "Genres"},
            {"name": "Characters"},
            {"name": "Companies"},
            {"name": "People"},
            {"name": "Favourite"},
            {"name": "Watch"},
            {"name": "Read"},
            {"name": "Related"},
            {"name": "Edit"},
            {"name": "Settings"},
            {"name": "Schedule"},
            {"name": "Upload"},
            {"name": "Comments"},
            {"name": "Notifications"},
            {"name": "Integrations"},
            {"name": "Collections"},
            {"name": "History"},
            {"name": "Stats"},
            {"name": "Vote"},
        ],
        lifespan=lifespan,
        # redoc_url=None,
        # docs_url=None,
    )

    app.add_middleware(TimeoutMiddleware, timeout=60)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_profiling_middleware(app)

    app.add_exception_handler(errors.Abort, errors.abort_handler)
    app.add_exception_handler(
        RequestValidationError,
        errors.validation_handler,
    )

    from .notifications import router as notifications_router
    from .integrations import router as integrations_router
    from .collections import router as collections_router
    from .characters import router as characters_router
    from .companies import router as companies_router
    from .favourite import router as favourite_router
    from .settings import router as settings_router
    from .comments import router as comments_router
    from .schedule import router as schedule_router
    from .articles import router as articles_router
    from .related import router as related_router
    from .history import router as history_router
    from .genres import router as genres_router
    from .upload import router as upload_router
    from .people import router as people_router
    from .follow import router as follow_router
    from .system import router as system_router
    from .client import router as client_router
    from .anime import router as anime_router
    from .manga import router as manga_router
    from .novel import router as novel_router
    from .watch import router as watch_router
    from .stats import router as stats_router
    from .admin import router as admin_router
    from .read import router as read_router
    from .user import router as user_router
    from .auth import router as auth_router
    from .edit import router as edit_router
    from .vote import router as vote_router

    app.include_router(notifications_router)
    app.include_router(integrations_router)
    app.include_router(collections_router)
    app.include_router(characters_router)
    app.include_router(companies_router)
    app.include_router(favourite_router)
    app.include_router(settings_router)
    app.include_router(comments_router)
    app.include_router(schedule_router)
    app.include_router(articles_router)
    app.include_router(related_router)
    app.include_router(history_router)
    app.include_router(genres_router)
    app.include_router(upload_router)
    app.include_router(people_router)
    app.include_router(follow_router)
    app.include_router(system_router)
    app.include_router(client_router)
    app.include_router(admin_router)
    app.include_router(anime_router)
    app.include_router(manga_router)
    app.include_router(novel_router)
    app.include_router(watch_router)
    app.include_router(stats_router)
    app.include_router(read_router)
    app.include_router(user_router)
    app.include_router(auth_router)
    app.include_router(edit_router)
    app.include_router(vote_router)

    @app.get("/ping")
    async def ping_pong():
        return "pong"

    Instrumentator().instrument(app).expose(app)

    return app
