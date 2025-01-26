# Base stage for setting up Python and environment variables
FROM python:3.11-slim AS base

# Set PYTHONPATH and working directory in the container
ENV PYTHONPATH=/app/src:/app
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Create a non-root user
RUN useradd -m myuser

# Initial setup stage for installing system dependencies and audio drivers
FROM base AS init_pomodoro

# Temporarily switch to root to install system dependencies
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-mixer-2.0-0 \
    libglib2.0-dev \
    binutils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

RUN chown -R myuser:myuser /app/resources

# Declare /app/resources/logs as a volume
VOLUME /app/resources

# Switch back to the non-root user
USER myuser
# Stage for installing Pomodoro dependencies (excluding development dependencies)
FROM init_pomodoro AS pomodoro
ARG MODULE_GROUP
# Install only the necessary dependencies for running the Pomodoro app
RUN poetry install --with ${MODULE_GROUP} --without dev --no-interaction --no-ansi -vvv

# Stage for installing development dependencies
FROM init_pomodoro AS pomodoro-test
ARG MODULE_GROUP
# Set environment variables to use a dummy audio driver
ENV SDL_AUDIODRIVER=dummy
ENV AUDIODEV=null
# Install all dependencies, including development, for testing
RUN poetry install --with ${MODULE_GROUP} --no-interaction --no-ansi -vvv
