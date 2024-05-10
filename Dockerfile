# Build stage
FROM python:3.10-slim AS builder
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml .
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi
COPY . .

# Working stage
FROM python:3.10-slim AS production
WORKDIR /app
ENV PYTHONPATH=/app
ENV PYTHONDONOTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY --from=builder /app /app