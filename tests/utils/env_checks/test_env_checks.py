import os
import pytest
import sys
from unittest.mock import Mock, patch
from src.utils.env_checks.env_checks import (
    get_env_var,
    get_running_in_pyinstaller,
    load_environment_variables,
)
from tests.shared_annotations import (
    mock_test_sys, mock_test_os, StandardTestCase,
    file_system_test
)
from src.utils.test import smart_mock


class TestEnvChecks(StandardTestCase):
    """Test class for environment checks using smart annotations."""

    def test_get_running_in_pyinstaller(self):
        """Test get_running_in_pyinstaller when running inside PyInstaller."""
        from unittest.mock import patch
        with patch.object(sys, 'frozen', True, create=True):
            with patch.object(sys, 'executable', "fake_executable_path"):
                path = get_running_in_pyinstaller()
                assert path == "fake_executable_path"

    @mock_test_os(environ={"TEST_VAR": "test_value"})
    def test_get_env_var(self):
        """Test getting an existing environment variable."""
        value = get_env_var("TEST_VAR")
        assert value == "test_value"

    @mock_test_os(environ={})  # Empty environment
    def test_get_env_var_missing(self):
        """Test getting missing environment variable raises KeyError."""
        with pytest.raises(KeyError, match="Environment variable 'NON_EXISTENT_VAR' not found"):
            get_env_var("NON_EXISTENT_VAR")

    @file_system_test(files_exist={"fake_env_file": True})
    def test_load_environment_variables_file_exists(self):
        """Test loading environment variables when file exists."""
        from unittest.mock import patch
        with patch('src.utils.env_checks.env_checks.dotenv_load_dotenv') as mock_dotenv:
            with patch('os.path.exists', return_value=True):
                # Call the function with file that exists
                load_environment_variables("fake_env_file")
                # Verify dotenv_load_dotenv was called with the correct filename
                mock_dotenv.assert_called_once_with("fake_env_file")

    @file_system_test(files_exist={"fake_env_file": False})
    def test_load_environment_variables_file_not_found(self):
        """Test loading environment variables when file doesn't exist."""
        from unittest.mock import patch
        with patch('src.utils.env_checks.env_checks.dotenv_load_dotenv') as mock_dotenv:
            with patch('os.path.exists', return_value=False):
                with pytest.raises(FileNotFoundError, match="fake_env_file not found"):
                    load_environment_variables("fake_env_file")
                # Verify dotenv_load_dotenv was not called in this case
                mock_dotenv.assert_not_called()

    def test_load_environment_variables_simple(self):
        """Test loading environment variables from default .env file."""
        from unittest.mock import patch
        with patch('src.utils.env_checks.env_checks.dotenv_load_dotenv') as mock_dotenv:
            with patch('os.path.exists', return_value=True):
                load_environment_variables()
                # Should call with default ".env" file
                mock_dotenv.assert_called_once_with(".env")
