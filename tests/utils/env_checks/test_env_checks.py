import pytest
from src.utils.env_checks.env_checks import (
    get_running_in_pyinstaller,
    get_env_var,
    load_environment_variables,
)


def test_get_running_in_pyinstaller(mock_sys):
    """Test get_running_in_pyinstaller when running inside PyInstaller."""
    # The mock_sys fixture is now a context manager that's already active
    path = get_running_in_pyinstaller()  # Assuming this checks sys.executable
    assert path == "fake_executable_path"


def test_get_env_var(mock_os):
    # The mock_os fixture is now a context manager that's already active
    value = get_env_var("TEST_VAR")
    assert value == "test_value"
    
    with pytest.raises(
        KeyError, match="Environment variable " "'NON_EXISTENT_VAR' not found"
    ):
        get_env_var("NON_EXISTENT_VAR")


def test_load_environment_variables_file_exists(mock_os):
    # The mock is already active
    load_environment_variables("fake_env_file")

    # Temporarily change the path.exists behavior to False
    with mock_os.update_patch("path.exists", False):
        with pytest.raises(FileNotFoundError, match="fake_env_file not found"):
            load_environment_variables("fake_env_file")
