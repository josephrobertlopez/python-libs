import os
import sys
from dotenv import load_dotenv as dotenv_load_dotenv


def get_running_in_pyinstaller() -> str:
    """Check if the script is running in a PyInstaller bundle.

    Returns:
        str: Path to the executable if running in PyInstaller.

    Raises:
        EnvironmentError: If not running in a PyInstaller bundle.
    """
    if getattr(sys, "frozen", False):
        return sys.executable
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


def get_path_based_env_var(var_name: str) -> str:
    """Get an environment variable based on root path.

    Handles path separators for cross-platform compatibility.

    Args:
        var_name (str): The name of the environment variable to retrieve.

    Returns:
        str: Value of the environment variable properly joined with base path if needed.

    Raises:
        KeyError: If the environment variable is not found.
    """
    try:
        # Get the raw value from environment
        var = os.environ[var_name]

        # If path contains separators from the wrong OS, normalize them
        var = var.replace('/', os.sep).replace('\\', os.sep)

        # If running in PyInstaller, prepend the _MEIPASS base directory
        if getattr(sys, "frozen", False):
            return os.path.join(sys._MEIPASS, var)
        else:
            # For regular execution, check if it's an absolute path already
            if os.path.isabs(var):
                return var
            # For relative paths, return as is (caller will resolve relative to their context)
            return var
    except KeyError:
        raise KeyError(f"Environment variable '{var_name}' not found.")


def load_environment_variables(env_file: str = ".env") -> None:
    """Load environment variables from a specified .env file.

    Args:
        env_file (str): The path to the .env file to load.
    """
    if not os.path.exists(env_file):
        raise FileNotFoundError(f"{env_file} not found.")

    dotenv_load_dotenv(env_file)
    print(f"Environment variables loaded from {env_file}")
