import os
import pytest
from unittest import mock
from src.utils.env_checks.env_checks import (
    get_running_in_pyinstaller,
    get_env_var,
    load_environment_variables,
)


def test_get_running_in_pyinstaller(mock_sys):
    """Test get_running_in_pyinstaller when running inside PyInstaller."""
    path = get_running_in_pyinstaller()  # Assuming this checks sys.executable
    assert path == mock_sys.get_mock_obj("executable")

    with pytest.raises(EnvironmentError):
        mock_sys.remove_patch("frozen")
        get_running_in_pyinstaller()


def test_get_env_var():
    with mock.patch.dict(os.environ, {"TEST_VAR": "test_value"}):
        value = get_env_var("TEST_VAR")
        assert value == "test_value"
    with pytest.raises(KeyError, match="Environment variable "
                                       "'NON_EXISTENT_VAR' not found"):
        get_env_var("NON_EXISTENT_VAR")


def test_load_environment_variables_file_exists():
    """Test load_environment_variables loads variables
        from a .env_checks file."""
    with mock.patch("os.path.exists", return_value=True):
        with mock.patch(
                "src.utils.env_checks.env_checks.load_dotenv"
        ) as mock_load_dotenv:
            load_environment_variables("fake_env_file")
            mock_load_dotenv.assert_called_once()

    """Test load_environment_variables raises FileNotFoundError if
        .env_checks file is missing."""
    with mock.patch("os.path.exists", return_value=False):
        with mock.patch("dotenv.load_dotenv", return_value=True):
            with pytest.raises(FileNotFoundError,
                               match="fake_env_file not found"):
                load_environment_variables("fake_env_file")
