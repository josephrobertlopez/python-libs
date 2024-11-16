from src.pomodoro.pomodoro import main
import pytest


def test_main(mock_pomodoro_deps, mock_sleep):
    """Test main method of pomodoro."""
    SOUND_FILE = "resources/sounds/alarm_sound.wav"

    mock_get_env_var = mock_pomodoro_deps.get_mock_obj("get_env_var")
    mock_play_alarm_sound = mock_pomodoro_deps.get_mock_obj("play_alarm_sound")

    # Test valid input
    main("-m", "25")
    mock_sleep.assert_called_once_with(25 * 60)
    mock_get_env_var.assert_called_once_with("SOUND_FILE")
    mock_play_alarm_sound.assert_called_once_with(SOUND_FILE)

    # Test invalid integer input
    mock_pomodoro_deps.reset_mocks()
    mock_sleep.reset_mock()
    main("-m", "0")

    # Test with non integer input
    mock_pomodoro_deps.reset_mocks()
    mock_sleep.reset_mock()
    assert pytest.raises(SystemExit, main, "-m", "'a'").value.code == 2
