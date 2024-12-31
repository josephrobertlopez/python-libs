from unittest.mock import Mock, patch

import pytest

from src.utils.abstract.abstract_singleton import (
    AbstractSingleton,
    SampleConcreteSingleton,
)
from src.utils.media.audio import PygameMixerSoundSingleton
from src.utils.test.MockContextManager import MockContextManager


@pytest.fixture
def mock_sys():
    """
    Preconfigured MockFixture for sys module.
    """
    default_attr = {
        "frozen": True,
        "executable": "fake_executable_path",
        "_MEIPASS": "pyinstaller/path",
    }
    return MockContextManager(target_path="sys", attribute_values=default_attr)


@pytest.fixture
def mock_os():
    default_behaviors = {
        "path.exists": True,
        "environ": {"TEST_VAR": "test_value"},
        "path.join": lambda *args: "/".join(map(str, args)),
        "makedirs": True,
    }
    return MockContextManager(target_path="os", method_behaviors=default_behaviors)


@pytest.fixture
def mock_builtins():
    default_behaviors = {"open": Mock(), "print": Mock()}
    return MockContextManager(
        target_path="builtins", method_behaviors=default_behaviors
    )


@pytest.fixture
def mock_logging():
    """Fixture to mock logging setup."""
    mock_behaviors = {"getLogger": Mock(), "config.fileConfig": Mock()}
    return MockContextManager("logging", method_behaviors=mock_behaviors)


@pytest.fixture
def mock_context():
    """Fixture to set up common mock context for tests."""
    return {
        "target_path": "tests.utils.test.test_mockcontextmanager",
        "method_behaviors": {"method_name": lambda x: x * 2},
        "attribute_values": {"attr_name": 42},
        "mapping_values": {"map_name": {"key": "value"}},
    }


@pytest.fixture
def mock_pomodoro_deps():
    mock_path = "src.pomodoro.pomodoro"
    SOUND_FILE = "resources/sounds/alarm_sound.wav"
    default_behaviors = {
        "get_env_var": SOUND_FILE,
        "play_alarm_sound": None,
    }
    return MockContextManager(target_path=mock_path, method_behaviors=default_behaviors)


@pytest.fixture
def sample_concrete_singleton():
    """Fixture to instantiate the SampleConcreteSingleton."""
    return SampleConcreteSingleton()


@pytest.fixture
def pygame_mixer_audio():
    """Fixture to provide a PygameMixerAudio instance with mocked dependencies."""
    # set up the mock behaviors for methods you want to mock
    method_behaviors = {
        "init": Mock(),
        "music.get_busy": False,
        "music.play": Mock(),
        "music.pause": Mock(),
        "music.set_volume": Mock(),
    }

    class_values = {"Sound": {"get_num_channels": 1}}
    manager = MockContextManager(
        target_path="pygame.mixer",
        method_behaviors=method_behaviors,
        class_values=class_values,
    )
    return manager


@pytest.fixture
def mixer(pygame_mixer_audio):
    """Fixture to initialize PygameMixerAudio instance."""
    # Initialize PygameMixerAudio instance before each test
    mixer = PygameMixerSoundSingleton()
    # Ensure the singleton is set up in the context
    with pygame_mixer_audio:
        yield mixer


@pytest.fixture()
def mock_singleton_setup():
    """Fixture to mock AbstractSingleton setup and ensure it's called only once."""
    # Patch the setup method in AbstractSingleton to prevent the singleton check
    with patch.object(AbstractSingleton, "setup", Mock()) as mock_setup:
        # Ensure the singleton is set up before each test
        mock_setup()
        yield mock_setup
        # After each test, delete the setup to ensure it does not interfere with other tests
        del mock_setup
