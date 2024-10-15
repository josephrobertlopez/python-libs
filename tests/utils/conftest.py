# tests/conftest.py

import pytest
import pygame

@pytest.fixture
def mock_pygame_init(mocker):
    """Fixture to mock pygame.mixer.init."""
    return mocker.patch('pygame.mixer.init', autospec=True)

@pytest.fixture
def mock_get_init(mocker):
    """Fixture to mock pygame.mixer.get_init."""
    return mocker.patch('pygame.mixer.get_init', return_value=True, autospec=True)

@pytest.fixture
def mock_sound(mocker):
    """Fixture to mock pygame.mixer.Sound."""
    return mocker.patch('pygame.mixer.Sound', autospec=True)

@pytest.fixture
def mock_get_busy(mocker):
    """Fixture to mock pygame.mixer.get_busy."""
    return mocker.patch('pygame.mixer.get_busy', side_effect=[True, False], autospec=True)

@pytest.fixture
def mock_sound_loading_error(mocker):
    """Fixture to mock pygame.mixer.Sound to raise an error when loading sound."""
    return mocker.patch('pygame.mixer.Sound', side_effect=pygame.error("Error loading sound"))

@pytest.fixture
def mock_file_staging(mocker):
    """Generic fixture to mock file staging components."""

    # Mock os.makedirs to simulate creting the log directory
    mock_makedirs = mocker.patch('os.makedirs', autospec=True)

    # Mock os.path.exists to simulate checking if the log file exists
    mock_exists = mocker.patch('os.path.exists', autospec=True)

    # Mock open to simulate creating the log file
    mock_open = mocker.patch('builtins.open', autospec=True)

    return mock_makedirs, mock_exists, mock_open


@pytest.fixture
def mock_file_staging_with_logging(mocker, mock_file_staging):
    """Fixture that extends mock_file_staging to add logging functionality."""
    mock_makedirs, mock_exists, mock_open = mock_file_staging

    # Additional mocking logic for logging
    mock_log = mocker.patch('logging.Logger.info', autospec=True)

    # Mock logging configuration file loading
    mock_file_config = mocker.patch('logging.config.fileConfig', autospec=True)

    # Set up side effect for mock_exists to simulate that log files do not exist
    def mock_exists_side_effect(path):
        return path == 'resources/logs'  # Only return True for the directory, not for files

    mock_exists.side_effect = mock_exists_side_effect

    return mock_makedirs, mock_exists, mock_open, mock_log, mock_file_config