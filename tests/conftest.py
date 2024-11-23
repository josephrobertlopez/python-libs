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


# MockFixture for `os.path`
@pytest.fixture
def mock_os_path():
    """Mock fixture for `os.path` methods using MockFixture."""
    mock_paths = {
        "exists": lambda path: path,
        "abspath": lambda _: f"/mocked/path/"
    }
    with MockFixture("os.path", mock_paths) as mock_os:
        yield mock_os


# MockFixture for `sys` attributes
@pytest.fixture
def mock_sys():
    """Mock fixture for `sys` module."""
    mock_paths ={"__dict__" :{
        "frozen": False,
        "_MEIPASS": "/mocked/pyinstaller",  # Ensure this is a string, not a MagicMock
        "executable": "fake_executable_path"
    }}
    with MockFixture("sys", mock_paths) as s:
        yield s

