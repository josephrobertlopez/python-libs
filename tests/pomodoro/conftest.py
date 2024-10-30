import pytest


import pytest

@pytest.fixture
def mock_play_alarm_sound(mocker):
    """Fixture to mock the play_alarm_sound function."""
    # Create a mock for play_alarm_sound
    play_alarm_sound_mock = mocker.patch('src.pomodoro.pomodoro.play_alarm_sound', autospec=True)

    # Define a setter function to configure the return value of the mock
    def _set_play_sound(return_value=None):
        """Set the return value for the play_alarm_sound mock."""
        play_alarm_sound_mock.return_value = return_value

    # Yield the mock object and the setter function
    yield play_alarm_sound_mock, _set_play_sound

@pytest.fixture
def mock_get_env_var(mocker):
    """Fixture to mock the get_env_var function."""
    # Create a mock for get_env_var
    get_env_var_mock = mocker.patch('src.pomodoro.pomodoro.get_env_var', autospec=True)

    # Define a setter function to configure the return value of the mock
    def _set_get_env_var(return_value=None):
        """Set the return value for the get_env_var mock."""
        get_env_var_mock.return_value = return_value

    # Yield the mock object and the setter function
    yield get_env_var_mock, _set_get_env_var
