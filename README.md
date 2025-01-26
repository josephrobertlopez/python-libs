# Project Name

A brief description of what your project does.

## Features

- Feature 1
- Feature 2
- Feature 3

## Requirements

- Python 3.11+ (or whatever Python version your project supports)
- Poetry (for dependency management)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/yourproject.git
    cd yourproject
    ```

2. Install [Poetry](https://python-poetry.org/docs/#installation):

    If you don't have Poetry installed, you can install it by running:

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

3. Install project dependencies:

    ```bash
    poetry install
    ```

    This will create a virtual environment and install all dependencies specified in `pyproject.toml`.

## Usage

To activate the virtual environment and start working on the project:

```bash
# Set env vars

# Run pytest
docker-compose build --no-cache run-pytest 
docker-compose run --rm run-pytest 

# Run Behave
export MODULE_GROUP=pomodoro
export FEATURE=pomodoro

docker-compose build --no-cache pomodoro-behave
docker-compose run --rm pomodoro-behave

# Run app
export $MIN=0
export MODULE_GROUP=pomodoro
docker-compose --profile pomodoro-app run --rm pomodoro-app 

# Run on local
EXPORT MODULE_GROUP=pomodoro
poetry install --with $MODULE_GROUP --no-interaction --no-ansi -vvv
poetry run python -m run $MODULE_GROUP --minutes 0
