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
# Build tests

docker-compose build --no-cache pomodoro-pytest 
docker-compose run --rm pomodoro-pytest 

docker-compose build --no-cache pomodoro-behave
docker-compose run --rm pomodoro-behave

# Build executable
docker-compose build --no-cache pomodoro-pyinstaller
docker-compose run --rm pomodoro-pyinstaller

# Run app
MINS=0 docker-compose --profile pomodoro-app run --rm pomodoro-app 