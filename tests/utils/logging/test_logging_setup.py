import sys

import pytest
from src.utils.logging.logging_config_singleton import LoggingConfigSingleton


@pytest.fixture
def get_singleton():
    logging_setup = LoggingConfigSingleton(
        config_path="path/to/config.ini", log_files=["app.log"]
    )
    yield logging_setup


def test_logging_setup_logging_file_dne(
    get_singleton, mock_os, mock_builtins, mock_logging
):
    # Create a mock function that returns False for 'resources/logs/app.log' and True for anything else
    def mock_path_exists(path):
        return path != "resources/logs/app.log"

    with mock_os.update_patch(
        "path.exists", mock_path_exists
    ) as mock_exists, mock_builtins, mock_logging:
        get_singleton.setup()
        mock_exists.assert_called_once_with("resources/logs/app.log")
        mock_builtins.get_mock("open").assert_called_once_with(
            "resources/logs/app.log", "w"
        )


def test_logging_setup(get_singleton, mock_os, mock_builtins, mock_logging):
    # if log file path exists, don't open
    with mock_os, mock_builtins, mock_logging:
        get_singleton._setup()
        sys.stderr.write("Test stderr redirection.\n")
        sys.stderr.flush()
        mock_builtins.get_mock("open").assert_not_called()


def test_logging_failed_config_load(get_singleton, mock_builtins, mock_logging):
    with mock_logging.remove_patch("config.fileConfig"), pytest.raises(RuntimeError):
        get_singleton.setup()
