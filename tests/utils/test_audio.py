# tests/utils/test_audio.py

import pytest
from src.utils.audio import play_alarm_sound


def test_play_alarm_sound_success(mock_pygame_init, mock_get_init, mock_sound, mock_get_busy):
    """Test play_alarm_sound with a valid sound file."""
    sound_file = "resources/sounds/alarm_sound.wav"

    play_alarm_sound(sound_file)

    mock_pygame_init.assert_called_once()
    # Assert that the sound was called once with the correct path
    mock_sound.assert_called_once()
    assert sound_file in mock_sound.call_args[0][0]

    mock_get_busy.assert_called()


def test_play_alarm_sound_mixer_not_initialized(mock_get_init, mock_pygame_init):
    """Test play_alarm_sound when mixer is not initialized."""
    # Simulate mixer not initialized
    mock_get_init.return_value = False

    with pytest.raises(RuntimeError):
        play_alarm_sound("resources/sounds/alarm_sound.wav")


def test_play_alarm_sound_error_loading_sound(mock_get_init, mock_pygame_init, mock_sound_loading_error):
    """Test play_alarm_sound when there is an error loading the sound file."""
    sound_file = "resources/sounds/alarm_sound.wav"

    with pytest.raises(RuntimeError):
        play_alarm_sound(sound_file)
