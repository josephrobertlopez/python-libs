# Use an official Python runtime as a parent image
FROM python:3.11-slim AS base

# Set PYTHONPATH
ENV PYTHONPATH=/app/src:/app

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required by pygame, pyinstaller, curl, and xz-utils
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-mixer-2.0-0 \
    libglib2.0-dev \
    binutils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables to use a dummy audio driver
ENV SDL_AUDIODRIVER=dummy
ENV AUDIODEV=null

# Copy the current directory contents into the container at /app
COPY . /app

# Install Poetry
RUN pip install poetry

# Stage for installing pomodoro dependencies
FROM base AS pomodoro
ARG MODULE_GROUP
RUN poetry install --only=${MODULE_GROUP} --without dev --no-interaction --no-ansi -vvv

# Stage for installing development dependencies
FROM base AS pomodoro-test
ARG MODULE_GROUP
RUN poetry install --with ${MODULE_GROUP} --no-interaction --no-ansi -vvv

## Stage for PyInstaller binary creation
FROM base AS pyinstaller-binary
ARG MODULE_GROUP

# Create a non-root user
RUN useradd -m myuser

# Change ownership of the app directory to myuser
RUN chown -R myuser:myuser /app

# Switch to non-root user
USER myuser

# Install pyinstaller
RUN poetry install --with ${MODULE_GROUP} --no-interaction --no-ansi -vvv