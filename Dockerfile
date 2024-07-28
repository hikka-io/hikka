FROM python:3.11-slim-buster

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /project

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

COPY sync.py .
COPY app ./app

CMD poetry run gunicorn "app:create_app()" --workers 4 --worker-class uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
