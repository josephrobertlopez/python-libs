import os
import unittest.mock

import pytest
from src.utils.env_checks.env_checks import (
    get_env_var,
    get_running_in_pyinstaller,
    load_environment_variables,
)
from src.utils.test.smart_mock import smart_mock


def test_get_running_in_pyinstaller(mock_sys):
    """Test get_running_in_pyinstaller when running inside PyInstaller."""
    # The mock_sys fixture is now a context manager that's already active
    path = get_running_in_pyinstaller()  # Assuming this checks sys.executable
    assert path == "fake_executable_path"


def test_get_env_var(mock_os):
    # Test getting an existing environment variable
    value = get_env_var("TEST_VAR")
    assert value == "test_value"

    # Create a direct patch for os.environ that will raise KeyError for the missing key
    # by using a MagicMock with a __getitem__ that raises KeyError for the specific key
    import unittest.mock
    environ_mock = unittest.mock.MagicMock()

    def getitem(key):
        if key == "NON_EXISTENT_VAR":
            raise KeyError(f"Environment variable '{key}' not found.")
        return "default"
    environ_mock.__getitem__.side_effect = getitem

    # Apply the patch directly
    with unittest.mock.patch("os.environ", environ_mock):
        with pytest.raises(KeyError, match="Environment variable 'NON_EXISTENT_VAR' not found"):
            get_env_var("NON_EXISTENT_VAR")


def test_load_environment_variables_file_exists(mock_os, mock_dotenv):
    # Configure mock_os.path.exists to return True for our test file
    with mock_os.update_patch("path.exists", lambda path: path == "fake_env_file"):
        # Call the function with file that exists
        load_environment_variables("fake_env_file")

        # Verify dotenv_load_dotenv was called with the correct filename
        mock_dotenv.assert_called_once_with("fake_env_file")

        # Reset the mock for the second test
        mock_dotenv.reset_mock()

        # Configure path.exists to return False for the next part
        with mock_os.update_patch("path.exists", lambda path: False):
            # Test that FileNotFoundError is raised for non-existent file
            with pytest.raises(FileNotFoundError, match="fake_env_file not found"):
                load_environment_variables("fake_env_file")

            # Verify dotenv_load_dotenv was not called in this case
            mock_dotenv.assert_not_called()


# Simpler test without relying on the mock_os fixture
def test_load_environment_variables_simple():
    # Create a mock for dotenv.load_dotenv
    with unittest.mock.patch('src.utils.env_checks.env_checks.dotenv_load_dotenv') as mock_load_dotenv:
        # Create a mock for os.path.exists that returns True
        with unittest.mock.patch('os.path.exists', return_value=True):
            # Call the function
            load_environment_variables("fake_env_file")

            # Verify that load_dotenv was called with the correct argument
            mock_load_dotenv.assert_called_once_with("fake_env_file")


def test_load_environment_variables_file_not_found(mock_os, mock_dotenv):
    """Test loading environment variables when file doesn't exist."""
    # Configure mock_os.path.exists to return False for our test file
    with mock_os.update_patch("path.exists", return_value=False):
        load_environment_variables(".env")
        # Should still call dotenv even if file doesn't exist
        assert mock_dotenv.called
