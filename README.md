# Project Name

A brief description of what your project does.

## Features

- Feature 1
- Feature 2
- Feature 3

## Requirements

- Python 3.11+ (or whatever Python version your project supports)
- Poetry (for dependency management)
- Docker (for containerization and ease of deployment)

## Installation

### Step 1: Clone the repository

```bash
git clone https://github.com/yourusername/yourproject.git
cd yourproject
```

### Step 2: Install [Poetry](https://python-poetry.org/docs/#installation)

If you don't have Poetry installed, you can install it by running:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Step 3: Install project dependencies

This will create a virtual environment and install all dependencies specified in `pyproject.toml`:

```bash
poetry install
```

## Usage

### Set environment variables

Before running any commands, you may need to set some environment variables depending on the task:

```bash
# Example:
export MODULE_GROUP=pomodoro
export MINUTES=0
```

### Running Tests

To run your tests using `pytest` in a Docker container:

1. **Build the Docker image**:

    ```bash
    docker-compose build --no-cache run_pytest
    ```

2. **Run pytest**:

    ```bash
    docker-compose run --rm run_pytest
    ```

### Running Behave Tests

To run your Behave tests in a Docker container:

1. **Set up the environment**:

    ```bash
    export MODULE_GROUP=pomodoro
    export FEATURE=pomodoro
    ```

2. **Build the Docker image**:

    ```bash
    docker-compose build --no-cache run_behave
    ```

3. **Run Behave**:

    ```bash
    docker-compose run --rm run_behave
    ```

### Running the Application

To run the application in Docker:

1. **Set up the environment**:

    ```bash
    export MODULE_GROUP=pomodoro
    export MINUTES=0
    ```

2. **Run the app with Docker Compose**:

    ```bash
    docker-compose --profile pomodoro-app run --rm run_app
    ```

### Running the Application Locally (without Docker)

To run the application locally using Poetry, follow these steps:

1. **Set the environment variable**:

    ```bash
    export MODULE_GROUP=pomodoro
    ```

2. **Install dependencies with Poetry**:

    ```bash
    poetry install --with $MODULE_GROUP --no-interaction --no-ansi -vvv
    ```

3. **Run the application**:

    ```bash
    poetry run python -m run $MODULE_GROUP --minutes 0
    ```

## Development

To work on the project, make sure to install all dependencies and activate the environment via Poetry. You can also run tests locally using:

```bash
poetry run pytest
```

Or to run Behave tests:

```bash
poetry run behave
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

pyinstaller --onefile \   feature/pomodoro.py ] 6:10 PM
    --add-data "resources:resources" \
    --add-data ".env:." \
    --hidden-import "src.utils.module.ModuleRunnerSingleton" \
    --hidden-import "src.pomodoro.pomodoro" \
    run.py
