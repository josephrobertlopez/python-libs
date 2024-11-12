from src.pomodoro.pomodoro import main


def test_main_positive_minutes(mock_pomodoro_deps, mock_sleep):
    """Test with valid positive minutes."""
    # Use `MockFixture` to mock `get_env_var` and `play_alarm_sound`
    # Run the main function with positive minutes argument
    main("-m", "26")

    # Assert that `time.sleep` was called with the correct duration
    mock_sleep.assert_called_once_with(26 * 60)

    # Assert that `get_env_var` was called with "SOUND_FILE"
    (mock_pomodoro_deps.get_mock_obj("get_env_var")
     .assert_called_once_with("SOUND_FILE"))

    # Assert that `play_alarm_sound` was called with "alarm.wav"
    (mock_pomodoro_deps.get_mock_obj("play_alarm_sound")
     .assert_called_once_with("resources/sounds/alarm_sound.wav"))
