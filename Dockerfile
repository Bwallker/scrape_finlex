FROM python:3.12

ARG PORT
ENV PORT=$PORT

RUN pip install poetry==1.7

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache


ADD pyproject.toml pyproject.toml
ADD poetry.lock poetry.lock
ADD README.md README.md
ADD scrape_finlex scrape_finlex

RUN --mount=type=cache,id=s/62e3d581-0944-47af-9ec9-bb14a9666c35-/tmp/poetry_cache,target=/tmp/poetry_cache poetry install --without dev --no-root

ENV VIRTUAL_ENV=/.venv \
    PATH="/.venv/bin:$PATH"

ENTRYPOINT poetry build && pip install dist/scrape_finlex-0.1.0-py3-none-any.whl && python -m scrape_finlex
