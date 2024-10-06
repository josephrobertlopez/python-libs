import pytest
import pygame
from src.pomodoro.pomodoro import play_alarm_sound

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

def test_play_alarm_sound_success(mock_pygame_init, mock_get_init, mock_sound, mock_get_busy, mocker):
    """Test play_alarm_sound with a valid sound file."""
    sound_file = "resources/sounds/alarm_sound.wav"
    
    play_alarm_sound(sound_file)

    mock_pygame_init.assert_called_once()
    mock_sound.assert_called_once_with(sound_file)
    mock_get_busy.assert_called()

def test_play_alarm_sound_mixer_not_initialized(mocker):
    """Test play_alarm_sound when mixer is not initialized."""
    mocker.patch('pygame.mixer.get_init', return_value=False)
    
    with pytest.raises(SystemExit):
        play_alarm_sound("resources/sounds/alarm_sound.wav")

def test_play_alarm_sound_error_loading_sound(mock_pygame_init, mock_get_init, mocker):
    """Test play_alarm_sound when there is an error loading the sound file."""
    sound_file = "resources/sounds/alarm_sound.wav"
    mocker.patch('pygame.mixer.Sound', side_effect=pygame.error("Error loading sound"))

    with pytest.raises(SystemExit):
        play_alarm_sound(sound_file)
