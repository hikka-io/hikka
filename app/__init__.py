from tortoise.contrib.fastapi import register_tortoise
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import fastapi.openapi.utils as fu
from fastapi import FastAPI
from . import errors
import config


def create_app() -> FastAPI:
    fu.validation_error_response_definition = errors.ErrorResponse.schema()

    app = FastAPI(docs_url=None, redoc_url=None)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(
        RequestValidationError,
        errors.validation_handler,
    )

    app.add_exception_handler(errors.Abort, errors.abort_handler)

    # from .favourite import router as favourite
    # from .search import router as search
    # from .follow import router as follow
    # from .anime import router as anime
    # from .watch import router as watch
    # from .user import router as user
    from .auth import router as auth

    # app.include_router(favourite)
    # app.include_router(search)
    # app.include_router(follow)
    # app.include_router(anime)
    # app.include_router(watch)
    # app.include_router(user)
    app.include_router(auth)

    register_tortoise(
        app,
        config=config.tortoise,
        add_exception_handlers=True,
        generate_schemas=True,
    )

    return app
