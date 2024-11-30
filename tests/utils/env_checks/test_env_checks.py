import os
import pytest
from unittest import mock
from src.utils.env_checks.env_checks import (
    get_running_in_pyinstaller,
    get_env_var,
    load_environment_variables,
)
from src.utils.test.MockManager import MockManager


def test_get_running_in_pyinstaller(mock_sys):
    """Test get_running_in_pyinstaller when running inside PyInstaller."""
    path = get_running_in_pyinstaller()  # Assuming this checks sys.executable
    assert path == 'fake_executable_path'

    with pytest.raises(AttributeError):
        mock_sys.remove_patch("frozen")
        get_running_in_pyinstaller()


def test_get_env_var(mock_os):
    with mock_os:
        value = get_env_var("TEST_VAR")
        assert value == "test_value"
    with pytest.raises(KeyError, match="Environment variable "
                                       "'NON_EXISTENT_VAR' not found"):
        get_env_var("NON_EXISTENT_VAR")



def test_load_environment_variables_file_exists(mock_os):
    with mock_os:
        load_environment_variables("fake_env_file")

    with pytest.raises(FileNotFoundError,
                       match="fake_env_file not found"):
        load_environment_variables("fake_env_file")
