FROM python:3.12

ARG PORT
ENV PORT=$PORT

RUN pip install poetry==1.7

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -\
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'\
    && apt-get -y update\
    && apt-get install -y google-chrome-stable

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
