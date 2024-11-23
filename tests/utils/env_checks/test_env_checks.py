import os
import sys
import pytest
from unittest import mock
from src.utils.env_checks.env_checks import (
    get_resource_path,
    get_running_in_pyinstaller,
    get_env_var,
    load_environment_variables,
)

import os
import sys
from unittest import mock
from src.utils.env_checks.env_checks import get_resource_path

import os
import sys
from unittest import mock
from src.utils.env_checks.env_checks import get_resource_path
from src.utils.test.MockFixture import MockFixture


def test_get_resource_path_exists(mock_os_path, mock_sys):
    """Test get_resource_path returns the correct path when resource exists."""

    get_resource_path("test/resource")
    mock_os_path.get_mock_obj("exists").assert_called_once_with(
        "/mocked/path/test/resource")


def test_get_running_in_pyinstaller(mock_sys):
    """Test get_running_in_pyinstaller when running inside PyInstaller."""
    path = get_running_in_pyinstaller()  # Assuming this checks sys.executable
    assert path == "fake_executable_path"

    # """Test get_running_in_pyinstaller raises EnvironmentError
    #     when not in PyInstaller."""
    # # Ensures 'frozen' is not set in sys
    # with mock.patch.dict('sys.__dict__', {}, clear=True):
    #     with pytest.raises(EnvironmentError,
    #                        match="Not running in a PyInstaller bundle"):
    #         get_running_in_pyinstaller()
    # with MockFixture("sys",{"frozen":True,"executable":"fake_executable_path"}) as m:
    #     path = get_running_in_pyinstaller()
    #     assert path == "fake_executable_path"




def test_get_env_var():
    with mock.patch.dict(os.environ, {"TEST_VAR": "test_value"}):
        value = get_env_var("TEST_VAR")
        assert value == "test_value"
    with pytest.raises(KeyError, match="Environment variable 'NON_EXISTENT_VAR' not found"):
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

