from unittest.mock import Mock

import pygame
import pytest

from src.utils.test.MockContextManager import MockContextManager


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
def mock_logging():
    """Fixture to mock logging setup."""
    return MockContextManager("logging",{"getLogger":Mock(),"config.fileConfig":Mock()})

