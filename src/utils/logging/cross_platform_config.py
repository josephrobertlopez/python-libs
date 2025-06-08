"""Cross-platform logging configuration generator."""

import os
import tempfile
from pathlib import Path


def generate_cross_platform_logging_config(log_dir: str = None) -> str:
    """
    Generate a cross-platform logging configuration file with proper paths.

    Args:
        log_dir: Custom log directory. Defaults to 'resources/logs'

    Returns:
        Path to the generated configuration file
    """
    if log_dir is None:
        log_dir = os.path.join("resources", "logs")

    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Use pathlib for cross-platform path handling
    log_file_path = Path(log_dir) / "app.log"

    # Convert to string with forward slashes (works on all platforms)
    log_file_str = str(log_file_path).replace(os.sep, "/")

    config_content = f"""[loggers]
keys=root

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler,fileHandler

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=DEBUG
formatter=simpleFormatter
args=('{log_file_str}', 'a')

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=%Y-%m-%d %H:%M:%S
"""

    # Create temporary config file
    config_file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".ini", prefix="logging_config_", delete=False
    )

    config_file.write(config_content)
    config_file.close()

    return config_file.name


def get_platform_info() -> dict:
    """Get current platform information for debugging."""
    return {
        "os_name": os.name,
        "platform_system": os.uname().sysname if hasattr(os, "uname") else "Unknown",
        "path_separator": os.sep,
        "path_delimiter": os.pathsep,
        "temp_dir": tempfile.gettempdir(),
    }
