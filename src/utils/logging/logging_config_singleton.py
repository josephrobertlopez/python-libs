import builtins  # Import builtins to override print
import logging
import logging.config
import os
import sys
from typing import List

from src.utils.logging.logger_stream import LoggerStream
from src.utils.abstract.abstract_singleton import AbstractSingleton
from src.utils.logging.cross_platform_config import (
    generate_cross_platform_logging_config,
)


class LoggingConfigSingleton(AbstractSingleton):
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of LoggingSingleton is created."""
        if cls._instance is None:
            cls._instance = super(LoggingConfigSingleton, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        config_path: str = None,
        log_dir: str = None,
        log_files: List[str] = None,
        use_cross_platform: bool = True,
    ):
        """Initialize logger setup."""
        if hasattr(self, "_initialized") and self._initialized:
            return  # Avoid reinitialization
        self._initialized = True  # Mark as initialized

        # Use os.path.join for default log directory
        self.log_dir = (
            log_dir if log_dir is not None else os.path.join("resources", "logs")
        )
        self.log_files = log_files or ["app.log", "error.log"]

        # Handle cross-platform configuration
        if use_cross_platform and (
            config_path is None or not os.path.exists(config_path)
        ):
            self.config_path = generate_cross_platform_logging_config(self.log_dir)
        else:
            self.config_path = config_path or os.path.join(
                "resources", "logging_config.ini"
            )

    @staticmethod
    def _custom_print(*args, **kwargs):
        message = " ".join(map(str, args))
        logging.info(message)

    @staticmethod
    def _initialize_log_files(log_dir, log_files) -> None:
        """Ensure log files exist."""
        os.makedirs(log_dir, exist_ok=True)
        for log_file in log_files:
            log_file_path = os.path.join(log_dir, log_file)
            if not os.path.exists(log_file_path):
                open(log_file_path, "w").close()

    @staticmethod
    def load_logging_config(config_path) -> None:
        """Load the logging configuration."""
        try:
            logging.config.fileConfig(config_path)
        except Exception as e:
            raise RuntimeError(
                f"Failed to load logging configuration from '{config_path}': {e}"
            )

    @staticmethod
    def redirect_print_to_logger(custom_printer=_custom_print) -> None:
        """Redirect print statements to the logger."""
        builtins.print = custom_printer

    @staticmethod
    def _redirect_stdout_stderr_to_logger() -> None:
        """Redirect stdout and stderr to the logger using the enhanced LoggerStream."""
        logger = logging.getLogger()
        sys.stdout = LoggerStream(logger.debug)
        sys.stderr = LoggerStream(logger.error)

    def _setup(self) -> None:
        """Perform the full logger setup."""
        self._initialize_log_files(self.log_dir, self.log_files)
        self.load_logging_config(self.config_path)
        self.redirect_print_to_logger()
        self._redirect_stdout_stderr_to_logger()
