import pytest
from src.utils.logging_setup import *
import os


def test_create_log_directory_failure(mock_file_staging):
    """Test create_log_directory handles failure to create directory."""
    mock_makedirs, _, _, _ = mock_file_staging
    mock_makedirs.side_effect = OSError("Failed to create directory")

    with pytest.raises(RuntimeError, match="Failed to create log directory"):
        create_log_directory('invalid/log/dir')


def test_initialize_log_files_creates_log_file(mock_file_staging):
    """Test that initialize_log_files creates a single log file."""
    mock_makedirs, mock_path_exists, mock_path_join, mock_open = mock_file_staging
    log_dir = 'resources/logs'
    log_file = 'app.log'

    mock_path_exists.return_value = False  # Simulate log file does not exist

    initialize_log_files(log_dir, [log_file])

    # Verify that open was called with the correct log file path
    expected_path = os.path.join(log_dir, log_file)
    mock_open.assert_called_once_with(expected_path, 'w')


def test_initialize_log_files_does_not_create_existing_file(mock_file_staging):
    """Test that initialize_log_files does not create an existing log file."""
    mock_makedirs, mock_path_exists, mock_path_join, mock_open = mock_file_staging
    log_dir = 'resources/logs'
    log_file = 'app.log'

    mock_path_exists.return_value = True  # Simulate log file exists

    initialize_log_files(log_dir, [log_file])

    # Verify that open was not called since the file exists
    mock_open.assert_not_called()


def test_load_logging_config_calls_file_config(mock_logging):
    """Test load_logging_config loads the logging configuration."""
    mock_log, mock_file_config = mock_logging
    config_path = 'resources/logging_config.ini'

    load_logging_config(config_path)

    # Verify that the logging configuration was loaded
    mock_file_config.assert_called_once_with(config_path)


def test_setup_logging_creates_log_directory(mock_file_staging, mock_logging):
    """Test setup_logging creates the log directory."""
    mock_makedirs, mock_path_exists, _, _ = mock_file_staging
    mock_path_exists.return_value = True  # Assume log files exist

    setup_logging("resources/logging_config.ini")

    # Verify that the log directory was created
    mock_makedirs.assert_called_once_with('resources/logs', exist_ok=True)


def test_setup_logging_loads_logging_config(mock_file_staging, mock_logging):
    """Test setup_logging loads logging configuration."""
    mock_file_config = mock_logging[1]

    mock_makedirs, mock_path_exists, mock_path_join, _ = mock_file_staging
    mock_path_exists.return_value = True  # Assume log files exist

    setup_logging("resources/logging_config.ini")

    # Verify that the logging configuration was loaded
    mock_file_config.assert_called_once()
    assert "logging_config.ini" in mock_file_config.call_args[0][0]


def test_log_uncaught_exceptions_logs_error(mock_logging):
    """Test uncaught exceptions are logged correctly."""
    mock_log, _ = mock_logging
    exc_type = ValueError
    exc_value = ValueError("Test exception")

    setup_logging("resources/logging_config.ini")

    log_uncaught_exceptions(exc_type, exc_value, None)

    # Verify that the error was logged
    mock_log.return_value.error.assert_called_once_with("Uncaught exception", exc_info=(exc_type, exc_value, None))
