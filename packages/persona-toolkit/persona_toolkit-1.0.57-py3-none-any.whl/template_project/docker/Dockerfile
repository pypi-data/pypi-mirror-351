FROM python:3.11-buster

RUN pip install poetry==2.1.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

ENV PORT=8000

WORKDIR /app

COPY pyproject.toml ./
COPY poetry.lock ./
COPY tools ./tools
COPY .env ./
COPY docker/run.sh ./
RUN chmod +x ./run.sh

RUN poetry install --no-root

ENTRYPOINT ["./run.sh"]