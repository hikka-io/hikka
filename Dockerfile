FROM python:3.12.5-alpine3.20 as base

ENV VIRTUAL_ENV=/project/.venv \
    PATH="/project/.venv/bin:$PATH"


FROM base as builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PIP_ROOT_USER_ACTION=ignore

RUN apk add gcc python3-dev musl-dev linux-headers

RUN pip install poetry==1.8.3

WORKDIR /project

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR



FROM base as runtime

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /project

COPY sync.py .
COPY aggregator.py .
COPY alembic ./alembic
COPY app ./app

CMD uvicorn app:create_app --host 0.0.0.0 --port 8000
