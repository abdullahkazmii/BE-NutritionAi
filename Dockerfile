# Use Python 3.12-slim base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install Poetry and dependencies
RUN apt-get update && apt-get install -y curl gcc libpq-dev \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry \
    && poetry --version


COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --only main

COPY app ./app
COPY .env .env

# Expose port
EXPOSE 8001

# Use uvicorn with hot reload
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

