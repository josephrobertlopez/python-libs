import pytest

from src.pomodoro.pomodoro import main


def test_main_function_with_mocks(
    mock_play_alarm_sound, mock_sleep, mock_argparse, mock_get_env_var
):
    """Test the main function with mocked play_alarm_sound and get_env_var."""
    sound_file = "resources/sounds/alarm_sound.wav"
    minutes = 5  # Test with 5 minutes

    # Unpack the mock objects and their setter functions
    _, set_args = mock_argparse
    play_alarm_sound_mock, set_play_sound = mock_play_alarm_sound
    _, set_get_env_var = mock_get_env_var

    # Set the return values using the setters
    set_args(minutes=minutes)
    set_play_sound(sound_file)
    set_get_env_var(sound_file)

    # Call the main function
    main()

    # Assertions to verify behavior
    play_alarm_sound_mock.assert_called_once_with(sound_file)
    mock_sleep.assert_called_once_with(minutes * 60)


def test_main_invalid_input(mock_argparse):
    """Test main function with invalid input."""
    input_value = "not_a_number"
    _, set_args = mock_argparse
    set_args(minutes=input_value)

    with pytest.raises(TypeError):
        main()
