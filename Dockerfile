# Use an official Python runtime as a parent image
FROM python:3.11-slim AS base

# Set PYTHONPATH
ENV PYTHONPATH=/app/src:/app

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required by pygame
RUN apt-get update && apt-get install -y \
    libsdl2-mixer-2.0-0 \
    libglib2.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables to use a dummy audio driver
# This will prevent SDL from trying to use ALSA or PulseAudio
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
