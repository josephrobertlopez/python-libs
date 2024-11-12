import pytest

from src.utils.test.MockFixture import MockFixture


@pytest.fixture
def mock_pomodoro_deps(mocker):
    """Fixture to mock pomodoro's deps"""
    default_behaviors = {
        "play_alarm_sound": lambda x: None,
        "get_env_var": "resources/sounds/alarm_sound.wav"
    }

    return MockFixture(mocker,
                       "src.pomodoro.pomodoro",
                       default_behaviors)
