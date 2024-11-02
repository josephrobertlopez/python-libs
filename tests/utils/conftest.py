import pygame
import pytest


@pytest.fixture
def mock_pygame_init(mocker):
    """Fixture to mock pygame.mixer.init."""
    return mocker.patch("pygame.mixer.init", autospec=True)


@pytest.fixture
def mock_get_init(mocker):
    """Fixture to mock pygame.mixer.get_init."""
    return mocker.patch(
        "pygame.mixer.get_init",
        return_value=True,
        autospec=True)


@pytest.fixture
def mock_sound(mocker):
    """Fixture to mock pygame.mixer.Sound."""
    return mocker.patch("pygame.mixer.Sound", autospec=True)


@pytest.fixture
def mock_get_busy(mocker):
    """Fixture to mock pygame.mixer.get_busy."""
    return mocker.patch(
        "pygame.mixer.get_busy", side_effect=[True, False], autospec=True
    )


@pytest.fixture
def mock_sound_loading_error(mocker):
    """Fixture to mock pygame.mixer.
    Sound to raise an error when loading sound."""
    return mocker.patch(
        "pygame.mixer.Sound", side_effect=pygame.error("Error loading sound")
    )


@pytest.fixture
def mock_file_staging(mocker):
    """Generic fixture to mock file staging components."""
    # Mock os.makedirs to simulate creating the log directory
    mock_makedirs = mocker.patch("os.makedirs", autospec=True)

    mock_path_exists = mocker.patch("os.path.exists", autospec=True)
    mock_path_join = mocker.patch("os.path.join", autospec=True)

    # Mock open to simulate creating the log file
    mock_open = mocker.patch("builtins.open", autospec=True)

    # Customize path joining for tests
    mock_path_join.side_effect = lambda *args: "/".join(args)

    return mock_makedirs, mock_path_exists, mock_path_join, mock_open


@pytest.fixture
def mock_logging(mocker):
    """Fixture to mock logging setup."""
    mock_log = mocker.patch("logging.getLogger")
    mock_file_config = mocker.patch("logging.config.fileConfig")
    return mock_log, mock_file_config
