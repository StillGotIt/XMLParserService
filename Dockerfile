FROM python:3.12-bookworm

ENV POETRY_VERSION=2.0.0

RUN pip install -U pip setuptools && \
    pip install poetry==${POETRY_VERSION}

WORKDIR /app

COPY pyproject.toml .

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . .

EXPOSE 8000