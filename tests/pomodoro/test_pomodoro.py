from src.pomodoro.pomodoro import main
import pytest


def test_main(mock_pomodoro_deps, mock_sleep):
    """Test main method of pomodoro."""
    mock_get_env_var = mock_pomodoro_deps.get_mock_obj("get_env_var")
    mock_play_alarm_sound = mock_pomodoro_deps.get_mock_obj("play_alarm_sound")

    # Test valid input
    main("-m", "25")
    mock_sleep.assert_called_once_with(25 * 60)
    mock_get_env_var.assert_called_once_with("SOUND_FILE")
    mock_play_alarm_sound.assert_called_once_with("resources/sounds/alarm_sound.wav")

    # Test invalid integer input
    mock_sleep.reset_mock()
    mock_pomodoro_deps.reset_mocks()
    main("-m", "-1")
    mock_play_alarm_sound.assert_not_called()
    mock_get_env_var.assert_not_called()

    # Test with non integer input
    mock_pomodoro_deps.reset_mocks()
    mock_sleep.reset_mock()
    assert pytest.raises(SystemExit, main, "-m", "'a'").value.code == 2
