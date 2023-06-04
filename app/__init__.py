from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import sessionmanager
import fastapi.openapi.utils as fu
from fastapi import FastAPI
from . import errors
import config


def create_app(init_db: bool = True) -> FastAPI:
    lifespan = None

    # SQLAlchemy initialization process
    if init_db:
        sessionmanager.init(config.database)

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield
            if sessionmanager._engine is not None:
                await sessionmanager.close()

    fu.validation_error_response_definition = errors.ErrorResponse.schema()

    app = FastAPI(
        # docs_url=None,
        # redoc_url=None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(RequestValidationError, errors.validation_handler)

    app.add_exception_handler(errors.Abort, errors.abort_handler)

    from .favourite import router as favourite_router
    from .follow import router as follow_router
    from .anime import router as anime_router
    from .watch import router as watch_router
    from .user import router as user_router
    from .auth import router as auth_router
    from .list import router as list_router

    app.include_router(favourite_router)
    app.include_router(follow_router)
    app.include_router(anime_router)
    app.include_router(watch_router)
    app.include_router(user_router)
    app.include_router(auth_router)
    app.include_router(list_router)

    return app
