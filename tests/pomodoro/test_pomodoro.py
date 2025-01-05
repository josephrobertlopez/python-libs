import pytest
from unittest.mock import patch, MagicMock
from src.pomodoro.pomodoro import PomodoroRunner


# Mocking os and environment variable for the sound file path
@pytest.fixture
def mock_os():
    with patch.dict("os.environ", {"SOUND_FILE": "test_sound_file.wav"}):
        yield


# Mocking PygameMixerSoundSingleton
@pytest.fixture
def mock_pygame_mixer(mock_singleton_setup):
    with patch("src.utils.media.audio.PygameMixerSoundSingleton") as mock_sound:
        mock_sound_instance = MagicMock()
        mock_sound.return_value = mock_sound_instance
        yield mock_sound_instance


# Mocking time.sleep
@pytest.fixture
def mock_time():
    with patch("time.sleep") as mock_sleep:
        yield mock_sleep


# Test PomodoroRunner behavior
def test_pomodoro_runner(mock_pygame_mixer, mock_time, mock_os, pygame_mixer_audio):
    # Initialize PomodoroRunner
    with pygame_mixer_audio:
        runner = PomodoroRunner()
        # Simulate passing arguments for minutes
        args = ["-m", "1"]  # 1-minute Pomodoro session

        # Run the main method
        runner.main(*args)
        mock_time.assert_called_once_with(60)
