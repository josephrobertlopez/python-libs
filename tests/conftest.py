import argparse
import sys

import pytest

from src.utils.test.MockFixture import MockFixture


@pytest.fixture
def mock_sleep(mocker):
    """Fixture to mock time.sleep to avoid actual delays."""
    return mocker.patch("time.sleep", autospec=True)


@pytest.fixture
def mock_sys_argv(mocker):
    """Fixture to mock sys.argv for testing main function."""

    # Patch `sys.argv`
    argv_mock = mocker.patch.object(sys, "argv", new=[])

    # Define a function to set sys.argv to specific test arguments
    def set_sys_argv(test_args):
        # Update the mock's value for sys.argv
        argv_mock[:] = test_args  # Modify the list in place

    # Yield the setter function and the mock object
    yield set_sys_argv, argv_mock


@pytest.fixture
def mock_argparse(mocker):
    # Patch `ArgumentParser` in `argparse` and configure `parse_args`
    # dynamically
    parser_mock = mocker.patch("argparse.ArgumentParser", autospec=True)

    # This nested function will allow setting specific return values for
    # `parse_args`
    def _set_args(**kwargs):
        # Set each argument value in the mock's `parse_args`
        parser_mock.return_value.parse_args.return_value = argparse.Namespace(
            **kwargs)

    # Return both the parser mock and the nested function
    yield parser_mock, _set_args

@pytest.fixture
def mock_os_path(mocker):
    """Mock fixture for `os.path` methods using MockFixture."""
    # Use MockFixture to mock both `os.path.exists` and `os.path.abspath`
    mock_paths = {
        "exists": True,
        "abspath": "/mocked/path"
    }
    with MockFixture(mocker, "os.path", default_behaviors=mock_paths) as mock_os:
        yield mock_os

