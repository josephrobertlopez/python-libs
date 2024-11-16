import pytest

from src.utils.test.MockFixture import MockFixture


@pytest.fixture
def mock_pomodoro_deps():
    """
    Provides a MockFixture instance pre-configured to mock
    specific dependencies in the Pomodoro module.

    Returns:
        MockFixture: The fixture used for mocking.
    """
    mock_path = "src.pomodoro.pomodoro"
    SOUND_FILE = "resources/sounds/alarm_sound.wav"
    default_behaviors = {
        "get_env_var": lambda _: SOUND_FILE,
        "play_alarm_sound": None,
    }
    # Initialize MockFixture
    return MockFixture(mock_path=mock_path,
                       default_behaviors=default_behaviors)
