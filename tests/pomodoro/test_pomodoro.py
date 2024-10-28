import pytest
from src.pomodoro.pomodoro import main


def test_main_valid_input(mock_play_alarm_sound, mock_sleep, mock_sys_argv):
    """Test main function with valid input."""
    minutes = 1
    test_args = [__file__, "-m", str(minutes)]
    mock_sys_argv(test_args)

    main()

    expected_sound_file = "resources/sounds/alarm_sound.wav"
    mock_play_alarm_sound.assert_called_once_with(expected_sound_file)
    mock_sleep.assert_called_once_with(minutes * 60)


def test_main_invalid_input(mock_sys_argv):
    """Test main function with invalid input."""
    input_value = "not_a_number"
    test_args = [__file__, "-m", input_value]
    mock_sys_argv(test_args)

    with pytest.raises(SystemExit):
        main()


def test_main_no_arguments(mock_sys_argv):
    """Test main function with no arguments."""
    test_args = [__file__]  # No arguments provided
    mock_sys_argv(test_args)

    with pytest.raises(SystemExit):
        main()
