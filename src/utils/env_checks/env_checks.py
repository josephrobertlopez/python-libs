import os
import sys
from typing import Dict

from dotenv import load_dotenv


def get_resource_path(relative_path: str) -> str:
    """Get the absolute path to a resource, works for
    development and PyInstaller.

    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: The full path to the resource.

    Raises:
        FileNotFoundError: If the resource is not found.
    """
    if getattr(sys, "frozen", False):  # Running in a PyInstaller bundle
        base_path = sys._MEIPASS  # PyInstaller's temp folder
    else:
        base_path = os.path.abspath("..")  # Current working directory

    full_path = os.path.join(base_path, relative_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Resource not found: {full_path}")

    return full_path


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
