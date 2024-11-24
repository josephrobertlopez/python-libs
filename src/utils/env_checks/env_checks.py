import os
import sys
from dotenv import load_dotenv


def get_running_in_pyinstaller() -> str:
    """Check if the script is running in a PyInstaller bundle.

    Returns:
        str: Path to the executable if running in PyInstaller.

    Raises:
        EnvironmentError: If not running in a PyInstaller bundle.
    """
    if getattr(sys, "frozen", False):
        return sys.executable  # Return the path to the executable
    raise EnvironmentError("Not running in a PyInstaller bundle.")


def get_env_var(var_name: str) -> str:
    """Get an environment variable.

    Args:
        var_name (str): The name of the environment variable to retrieve.

    Returns:
        str: Value of the environment variable.

    Raises:
        KeyError: If the environment variable is not found.
    """
    try:
        return os.environ[var_name]
    except KeyError:
        raise KeyError(f"Environment variable '{var_name}' not found.")


def load_environment_variables(env_file: str = ".env_checks") -> None:
    """Load environment variables from a specified .env_checks file.

    Args:
        env_file (str): The path to the .env_checks file to load.
    """
    if not os.path.exists(env_file):
        raise FileNotFoundError(f"{env_file} not found.")

    load_dotenv(env_file)
    print(f"Environment variables loaded from {env_file}")
