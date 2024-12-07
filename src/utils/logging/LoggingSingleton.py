import builtins  # Import builtins to override print
import logging
import logging.config
import os
import sys
from typing import List

from src.utils.logging.LoggerStream import LoggerStream


class LoggingSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of LoggingSingleton is created."""
        if cls._instance is None:
            cls._instance = super(LoggingSingleton, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path: str, log_dir: str = "resources/logs", log_files: List[str] = None):
        """Initialize logger setup."""
        if hasattr(self, '_initialized') and self._initialized:
            return  # Avoid reinitialization
        self._initialized = True  # Mark as initialized
        self.config_path = config_path
        self.log_dir = log_dir
        self.log_files = log_files or ["app.log", "error.log"]

    def initialize_log_files(self) -> None:
        """Ensure log files exist."""
        os.makedirs(self.log_dir, exist_ok=True)
        for log_file in self.log_files:
            log_file_path = os.path.join(self.log_dir, log_file)
            if not os.path.exists(log_file_path):
                open(log_file_path, "w").close()

    def load_logging_config(self) -> None:
        """Load the logging configuration."""
        try:
            logging.config.fileConfig(self.config_path)
        except Exception as e:
            raise RuntimeError(
                f"Failed to load logging configuration from '{self.config_path}': {e}"
            )

    @staticmethod
    def redirect_print_to_logger() -> None:
        """Redirect print statements to the logger."""

        def custom_print(*args, **kwargs):
            message = " ".join(map(str, args))
            logging.info(message)

        builtins.print = custom_print

    @staticmethod
    def redirect_stdout_stderr_to_logger() -> None:
        """Redirect stdout and stderr to the logger using the enhanced LoggerStream."""
        logger = logging.getLogger()
        sys.stdout = LoggerStream(logger.debug)
        sys.stderr = LoggerStream(logger.error)

    def setup(self) -> None:
        """Perform the full logger setup."""
        self.initialize_log_files()
        self.load_logging_config()
        self.redirect_print_to_logger()
        self.redirect_stdout_stderr_to_logger()
