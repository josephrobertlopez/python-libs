from unittest.mock import Mock, patch

import pytest
import os
from src.utils.abstract.abstract_runner import SampleConcreteRunner
from src.utils.abstract.abstract_singleton import (
    AbstractSingleton,
    SampleConcreteSingleton,
)
from src.utils.media.audio import PygameMixerSoundSingleton
from src.utils.test.smart_mock import smart_mock, patch_object, create_mock_class


@pytest.fixture
def mock_sys():
    """
    Preconfigured MockFixture for sys module.
    """
    with smart_mock(
        "sys",
        frozen=True,
        executable="fake_executable_path",
        _MEIPASS="pyinstaller/path",
        argv=["program_name"],
        stdout=Mock(),
        foo=Mock(),
    ) as mock_ctx:
        yield mock_ctx


@pytest.fixture
def mock_os():
    # Create a safe path joiner that won't cause recursion
    def path_join(*args):
        # Use the platform-specific separator
        sep = os.sep
        # Remove any leading/trailing separators from intermediate parts
        clean_parts = []
        for i, part in enumerate(args):
            if i == 0:
                clean_parts.append(part.rstrip(sep))
            elif i == len(args) - 1:
                clean_parts.append(part.lstrip(sep))
            else:
                clean_parts.append(part.strip(sep))
        return sep.join(clean_parts)
    
    with smart_mock(
        "os",
        **{
            "path.exists": True,
            "environ": {"TEST_VAR": "test_value", "LOG_CONFIG_FILE": "logging_config.ini"},
            "path.join": path_join,  # Use our custom path_join function
            "makedirs": True,
        }
    ) as mock_ctx:
        yield mock_ctx


@pytest.fixture
def mock_builtins():
    with smart_mock(
        "builtins",
        open=Mock(),
        print=Mock(),
    ) as mock_ctx:
        yield mock_ctx


@pytest.fixture
def mock_logging():
    """Fixture to mock logging setup."""
    with smart_mock(
        "logging",
        getLogger=Mock(),
        **{"config.fileConfig": Mock()}
    ) as mock_ctx:
        yield mock_ctx


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
def sample_concrete_singleton():
    """Fixture to instantiate the SampleConcreteSingleton."""
    return SampleConcreteSingleton()


@pytest.fixture
def sample_concrete_runner():
    """Fixture to instantiate SampleConcreteRunner."""
    return SampleConcreteRunner()


@pytest.fixture
def pygame_mixer_audio():
    """Fixture to provide a PygameMixerAudio instance with mocked dependencies."""
    # Use smart_mock to automatically detect the best mocking strategy
    with smart_mock(
        "pygame.mixer",
        init=Mock(),
        **{
            "music.get_busy": False,
            "music.play": Mock(),
            "music.pause": Mock(),
            "music.set_volume": Mock(),
            "Sound": create_mock_class(class_methods={"get_num_channels": 1})
        }
    ) as mock_ctx:
        yield mock_ctx


@pytest.fixture
def mixer(pygame_mixer_audio):
    """Fixture to initialize PygameMixerAudio instance."""
    # Initialize PygameMixerAudio instance before each test
    mixer = PygameMixerSoundSingleton()
    # Return the mixer within the mock context
    yield mixer


@pytest.fixture()
def mock_singleton_setup():
    """Fixture to mock AbstractSingleton setup and ensure it's called only once."""
    # Use patch_object instead of patch.object for more resilient mocking
    with patch_object(AbstractSingleton, "setup", Mock()) as mock_setup:
        # Ensure the singleton is set up before each test
        mock_setup()
        yield mock_setup
        # After each test, delete the setup to ensure it does not interfere with other tests
        del mock_setup


@pytest.fixture(autouse=True)
def setup_headless_audio():
    """Set up the headless audio environment for Pygame in CI."""
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    yield  # Allow tests to run
    del os.environ["SDL_AUDIODRIVER"]
