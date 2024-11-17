import os
import sys
import pytest
from unittest import mock
from src.utils.env_checks.env_checks import (
    get_resource_path,
    get_running_in_pyinstaller,
    get_virtual_env,
    get_env_var,
    get_docker_info,
    load_environment_variables,
)


def test_get_resource_path_exists(mock_os_path):
    """Test get_resource_path returns the correct path when resource exists."""
    get_resource_path("test/resource")

    mock_os_path.get_mock_obj("exists").assert_called_once_with(
        "/mocked/path/test/resource")


def test_get_running_in_pyinstaller():
    """Test get_running_in_pyinstaller when running inside PyInstaller."""
    with mock.patch.dict('sys.__dict__', {'frozen': True}):
        with mock.patch.object(sys, "frozen", create=True):
            with mock.patch.object(sys, "executable", "fake_executable_path"):
                path = get_running_in_pyinstaller()
                assert path == "fake_executable_path"


def test_get_running_in_pyinstaller_not_pyinstaller():
    """Test get_running_in_pyinstaller raises EnvironmentError
        when not in PyInstaller."""
    # Ensures 'frozen' is not set in sys
    with mock.patch.dict('sys.__dict__', {}, clear=True):
        with pytest.raises(EnvironmentError,
                           match="Not running in a PyInstaller bundle"):
            get_running_in_pyinstaller()


def test_get_virtual_env_venv():
    """Test get_virtual_env returns path if in a virtual environment."""
    with mock.patch.object(sys, "prefix", "fake_env_path"):
        with mock.patch.object(sys, "base_prefix", "different_path"):
            path = get_virtual_env()
            assert path == "fake_env_path"


def test_get_virtual_env_not_in_venv():
    """Test get_virtual_env raises EnvironmentError
        if not in a virtual environment."""
    with mock.patch.object(sys, "prefix", "fake_env_path"):
        with mock.patch.object(sys, "base_prefix", "fake_env_path"):
            with pytest.raises(EnvironmentError,
                               match="Not running in a virtual environment"):
                get_virtual_env()


def test_get_env_var_exists():
    """Test get_env_var returns the environment variable if it exists."""
    with mock.patch.dict(os.environ, {"TEST_VAR": "test_value"}):
        value = get_env_var("TEST_VAR")
        assert value == "test_value"


def test_get_env_var_not_exists():
    """Test get_env_var raises KeyError if the environment variable
        does not exist."""
    with pytest.raises(KeyError,
                       match="Environment variable "
                             "'NON_EXISTENT_VAR' not found"):
        get_env_var("NON_EXISTENT_VAR")


def test_get_docker_info_running():
    """Test get_docker_info returns Docker environment information
        if running in Docker."""
    with mock.patch("builtins.open", mock.mock_open(read_data="docker")):
        with mock.patch("os.path.exists", return_value=True):
            docker_info = get_docker_info()
            assert docker_info["running"] is True
            assert "container_id" in docker_info
            assert "hostname" in docker_info


def test_get_docker_info_not_running():
    """Test get_docker_info raises EnvironmentError
        if not running in Docker."""
    with mock.patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(EnvironmentError, match="Not running in Docker"):
            get_docker_info()


def test_load_environment_variables_file_exists():
    """Test load_environment_variables loads variables
        from a .env_checks file."""
    with mock.patch("os.path.exists", return_value=True):
        with mock.patch(
                "src.utils.env_checks.env_checks.load_dotenv"
        ) as mock_load_dotenv:
            load_environment_variables("fake_env_file")
            mock_load_dotenv.assert_called_once()


def test_load_environment_variables_file_not_exists():
    """Test load_environment_variables raises FileNotFoundError if
        .env_checks file is missing."""
    with mock.patch("os.path.exists", return_value=False):
        with mock.patch("dotenv.load_dotenv", return_value=True):
            with pytest.raises(FileNotFoundError,
                               match="fake_env_file not found"):
                load_environment_variables("fake_env_file")
