FROM python:3.12

ARG PORT
ENV PORT=$PORT

RUN pip install poetry==1.7

RUN apt-get install -y libglib2.0-0=2.50.3-2 \
    libnss3=2:3.26.2-1.1+deb9u1 \
    libgconf-2-4=3.2.6-4+b1 \
    libfontconfig1=2.11.0-6.7+b1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache


ADD pyproject.toml pyproject.toml
ADD poetry.lock poetry.lock
ADD README.md README.md
ADD scrape_finlex scrape_finlex

RUN poetry install --without dev --no-root

ENV VIRTUAL_ENV=/.venv \
    PATH="/.venv/bin:$PATH"

ENTRYPOINT poetry build && pip install dist/scrape_finlex-0.1.0-py3-none-any.whl && python -m scrape_finlex
