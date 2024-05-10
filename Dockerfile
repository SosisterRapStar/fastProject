FROM python:3.10-slim


WORKDIR /app


RUN pip install poetry

ENV PYTHONPATH=/app
ENV PYTHONPATH=/app/src
ENV PYTHONDONOTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY pyproject.toml .
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi

COPY . .


# ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
