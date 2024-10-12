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
poetry shell



# forward logs to local
docker run --device /dev/snd --privileged -v $(pwd)/resources/logs:/app/resources/logs my_pomodoro_image poetry run python -m src.pomodoro.pomodoro -m 25

# build container 
  docker build -f Dockerfile -t my_pomodoro_image .
docker run --rm --device /dev/snd --privileged my_pomodoro_image poetry run python -m src.pomodoro.pomodoro -m 0

# Build tests
docker build -f Dockerfile.dev -t my_pomodoro_image . 
  docker run --rm -it your_image_name  poetry run pytest  
docker run --rm --device /dev/snd --privileged my_pomodoro_image poetry run behave
