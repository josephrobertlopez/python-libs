import os
import logging
import logging.config
import sys
import builtins  # Import builtins to override print
from src.utils.environment import get_resource_path


def print_to_logger(message, level=logging.INFO):
    """Log print messages to the logger."""
    if message.strip():  # Avoid logging empty messages
        if level == logging.DEBUG:
            logging.debug(message)
        elif level == logging.WARNING:
            logging.warning(message)
        elif level == logging.ERROR:
            logging.error(message)
        else:
            logging.info(message)


def create_log_directory(log_dir: str) -> None:
    """Create the log directory if it doesn't exist."""
    try:
        os.makedirs(log_dir, exist_ok=True)
        print(f"Log directory created: {log_dir}")  # This will be redirected to logging
    except OSError as e:
        raise RuntimeError(f"Failed to create log directory '{log_dir}': {e}")


def initialize_log_files(log_dir: str, log_files: list) -> None:
    """Create log files if they don't exist."""
    for log_file in log_files:
        log_file_path = os.path.join(log_dir, log_file)
        if not os.path.exists(log_file_path):
            try:
                open(log_file_path, 'w').close()  # Create an empty log file
                print(f"Log file created: {log_file_path}")  # This will be redirected to logging
            except OSError as e:
                raise RuntimeError(f"Failed to create log file '{log_file_path}': {e}")


def load_logging_config(config_path: str) -> None:
    """Load logging configuration from the specified .ini file."""
    try:
        logging.config.fileConfig(config_path)
        print(f"Logging configuration loaded from: {config_path}")  # This will be redirected to logging
    except Exception as e:
        raise RuntimeError(f"Failed to load logging configuration from '{config_path}': {e}")


def log_uncaught_exceptions(exc_type, exc_value, exc_traceback) -> None:
    """Log uncaught exceptions to the error log."""
    logger = logging.getLogger()
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def setup_logging() -> None:
    """Set up logging for the application."""
    if getattr(sys, 'frozen', False):  # Running as a PyInstaller executable
        logging.disable(logging.CRITICAL)  # Disable all logging
        return

    # Redirect print statements to logger
    original_print = print  # Save the original print function

    def new_print(*args, **kwargs):
        # Create a formatted message
        message = ' '.join(map(str, args))
        print_to_logger(message, level=logging.INFO)

    # Override the built-in print function
    builtins.print = new_print

    # Define the log directory and files
    log_dir = 'resources/logs'
    log_files = ['app.log', 'error.log']

    # Create the log directory
    create_log_directory(log_dir)

    # Initialize log files
    initialize_log_files(log_dir, log_files)

    # Load logging configuration
    config_path = get_resource_path('resources/logging_config.ini')
    load_logging_config(config_path)

    # Log a test message to confirm setup
    print("Logging setup complete.")

    # Set the global exception handler
    sys.excepthook = log_uncaught_exceptions


if __name__ == "__main__":
    setup_logging()
