# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required by pygame
RUN apt-get update && apt-get install -y \
    libsdl2-mixer-2.0-0 \
    libglib2.0-dev \
    libasound2-dev \
    alsa-utils \
    pulseaudio \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Create logs directory
RUN mkdir -p resources/logs

# Install Poetry
RUN pip install poetry

# Install the Python dependencies using Poetry
RUN poetry install --no-dev --no-interaction --no-ansi

# Set PYTHONPATH to include /app/src
ENV PYTHONPATH=/app/src
