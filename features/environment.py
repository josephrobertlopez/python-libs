# features/environment.py
from behave import fixture, use_fixture
from src.utils.logging_setup import setup_logging

def before_all(context):
    """Executed before any tests are run."""
    setup_logging()  # Set up logging for the tests
