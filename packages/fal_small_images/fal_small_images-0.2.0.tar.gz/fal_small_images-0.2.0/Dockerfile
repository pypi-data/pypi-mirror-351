# syntax=docker/dockerfile:1

## Stage 1: Use the official Python image from the Docker Hub for all image stages
# Python version must match what's in `pyproject.toml` and `.python-version`
FROM python:3.13-slim AS base

# Define environment variables for the user and group
ENV APP_USER=appusr
ENV APP_GROUP=appgrp

# Create a non-root user and group
RUN addgroup --system $APP_GROUP && adduser --system --ingroup $APP_GROUP $APP_USER

# Switch to the new user
USER $APP_USER

# Set the working directory
WORKDIR /usr/src/app

# Setup usage of the app venv (built in later stages)
ENV PATH="/usr/src/app/.venv/bin:$PATH" VIRTUAL_ENV="/usr/src/app/.venv"

# Copy `pyproject.toml`, as it could hold common base configs
COPY --chown=${APP_USER}:${APP_GROUP} ./pyproject.toml .

## Stage 2: Build the app's non-dev dependencies with `uv`
FROM base AS pre-dev

# Setup `uv` from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0 UV_NO_CACHE=1

# Install locked project dependencies into venv, excluding dev packages
RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --locked --no-install-project --no-dev

# Copy in all non-dev app code from local (make sure not to copy in tests)
COPY --chown=${APP_USER}:${APP_GROUP} ./main.py ./
COPY --chown=${APP_USER}:${APP_GROUP} ./routes ./routes

## Stage 3: Dev-only image with `uv` pre-installed
FROM pre-dev AS dev

# Install additional dev dependencies into venv
RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --locked --no-install-project

# Copy in additional dev code from local (including tests, etc.)
COPY --chown=${APP_USER}:${APP_GROUP} ./tests ./tests

## Stage 4: Final deployment image, derived from a fresh `base` copy (no `uv`)
FROM base AS final

# Copy over non-dev code and venv into the final container
COPY --from=pre-dev --chown=${APP_USER}:${APP_GROUP} /usr/src/app/ .

# Expose the port that the FastAPI app will be listening on
EXPOSE 8000

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
