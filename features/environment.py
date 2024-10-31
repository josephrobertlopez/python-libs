# features/environment.py
from src.utils.logging_setup import setup_logging


def before_all(context):
    """Executed before any tests are run."""
    setup_logging("resources/logging_config.ini")
