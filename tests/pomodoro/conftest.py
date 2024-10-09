import pytest

@pytest.fixture
def mock_play_alarm_sound(mocker):
    """Fixture to mock the play_alarm_sound function."""
    return mocker.patch('src.pomodoro.pomodoro.play_alarm_sound', autospec=True)

