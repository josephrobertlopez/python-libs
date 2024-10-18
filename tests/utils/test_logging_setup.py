import os
import pytest
from src.utils.logging_setup import setup_logging

@pytest.mark.parametrize("log_dir, log_files", [
    ('resources/logs', ['app.log', 'error.log']),
])
def test_setup_logging(mock_file_staging_with_logging, log_dir, log_files):
    """Test setup_logging initializes logging correctly with the specified log directory and log files."""
    
    # Unpack the extended mock_file_staging_with_logging fixture
    mock_makedirs, mock_exists, mock_open, mock_log, mock_file_config = mock_file_staging_with_logging

    # Call the function that should trigger file operations
    setup_logging()

    # Print out the calls to the mocks for inspection
    print("Mocked os.makedirs calls:", mock_makedirs.call_args_list)
    print("Mocked os.path.exists calls:", mock_exists.call_args_list)
    print("Mocked open calls:", mock_open.call_args_list)
    print("Mocked logging.Logger.info calls:", mock_log.call_args_list)
    print("Mocked logging.config.fileConfig calls:", mock_file_config.call_args_list)

    # Verify that makedirs was called with the correct directory path
    mock_makedirs.assert_called_once_with(log_dir, exist_ok=True)

    # Verify that the mocked open was called with the correct paths for log files
    for log_file in log_files:
        log_file_path = os.path.join(log_dir, log_file)
        mock_open.assert_any_call(log_file_path, 'w')

    # Verify that the logging configuration was loaded
    mock_file_config.assert_called_once_with('resources/logging_config.ini')

    # Ensure that the log files are not actually created during the test
    mock_open.assert_called()
