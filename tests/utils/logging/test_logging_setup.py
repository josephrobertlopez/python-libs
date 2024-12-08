import pytest
from src.utils.logging.LoggingSingleton import LoggingConfigSingleton


@pytest.fixture
def init_LoggingConfigSingleton():
    logging_setup = LoggingConfigSingleton(config_path="path/to/config.ini", log_files=["app.log"])
    return logging_setup


def test_initialize_log_files(init_LoggingConfigSingleton, mock_os, mock_builtins, mock_logging):
    """Test that initialize_log_files creates a single log file."""
    logging_setup = init_LoggingConfigSingleton
    mock_open = mock_builtins.get_mock("open")

    # if log file path DNE, `touch it`
    with mock_os.update_patch("path.exists", False) as mock_exists:
        logging_setup.setup()
        mock_exists.assert_called_once_with("resources/logs/app.log")
        mock_open.assert_called_once_with("resources/logs/app.log", "w")

    # if log file path exists, don't open
    with mock_os, mock_builtins:
        logging_setup.setup()
        mock_open.assert_not_called()

    with mock_logging.remove_patch("config.fileConfig"), pytest.raises(RuntimeError):
        logging_setup.setup()
