import pytest
import sys
from src.pomodoro.pomodoro import main

@pytest.fixture
def mock_play_alarm_sound(mocker):
    """Fixture to mock the play_alarm_sound function."""
    # Ensure we mock the function where it is imported in the module
    return mocker.patch('src.pomodoro.pomodoro.play_alarm_sound', autospec=True)

@pytest.fixture
def mock_sleep(mocker):
    """Fixture to mock time.sleep to avoid actual delays."""
    return mocker.patch("time.sleep", autospec=True)

def test_main_valid_input(mock_play_alarm_sound, mock_sleep, mocker):
    """Test main function with valid input."""
    minutes = 1
    test_args = [__file__, "-m", str(minutes)]
    mocker.patch.object(sys, 'argv', test_args)

    main()

    expected_sound_file = "resources/sounds/alarm_sound.wav"
    mock_play_alarm_sound.assert_called_once_with(expected_sound_file)

    mock_sleep.assert_called_once_with(minutes * 60)

def test_main_invalid_input(mocker):
    """Test main function with invalid input."""
    input_value = "not_a_number"
    test_args = [__file__, "-m", input_value]

    mocker.patch.object(sys, 'argv', test_args)

    with pytest.raises(SystemExit):
        main()

def test_main_no_arguments(mocker):
    """Test main function with no arguments."""
    test_args = [__file__]  # No arguments provided
    mocker.patch.object(sys, 'argv', test_args)

    with pytest.raises(SystemExit):
        main()
