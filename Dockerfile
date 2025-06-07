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
FROM base AS init_app

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

RUN chown -R myuser:myuser /app/features
# Declare /app/resources/logs as a volume
VOLUME /app/resources

# Switch back to the non-root user
USER myuser
# Stage for installing application dependencies (excluding development dependencies)
FROM init_app AS application
ARG MODULE_GROUP
# Install only the necessary dependencies for running the Pomodoro app
RUN poetry install --with ${MODULE_GROUP} --without dev --no-interaction --no-ansi -vvv

# Stage for installing development dependencies
FROM init_app AS app-test
ARG MODULE_GROUP
# Set environment variables to use a dummy audio driver
ENV SDL_AUDIODRIVER=dummy
ENV AUDIODEV=null
# Install all dependencies, including development, for testing
RUN poetry install --with ${MODULE_GROUP} --no-interaction --no-ansi -vvv


FROM init_app AS cdk-init
USER root
# Install required dependencies (curl, gnupg, ca-certificates) and Node.js
RUN apt-get update && apt-get install -y curl gnupg ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean


# Install specified versions of AWS CDK and AWS CDK Local globally
RUN npm install -g aws-cdk@${AWS_CDK_VERSION} aws-cdk-local@${AWS_CDK_LOCAL_VERSION}

# Install Python dependencies (e.g., aws-cdk-lib)
RUN pip install --no-cache-dir aws-cdk-lib

# Copy the rest of your project files into the container
COPY . .
