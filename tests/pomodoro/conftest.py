import pytest

from src.utils.test.MockContextManager import MockContextManager


@pytest.fixture
def mock_pomodoro_deps():
    mock_path = "src.pomodoro.pomodoro"
    SOUND_FILE = "resources/sounds/alarm_sound.wav"
    default_behaviors = {
        "get_env_var": SOUND_FILE,
        "play_alarm_sound": None,
    }
    return MockContextManager(target_path=mock_path,
                       method_behaviors=default_behaviors)
