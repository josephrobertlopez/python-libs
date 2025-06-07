import pytest
import os
from unittest.mock import Mock, patch
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
    """Fixture to mock os module for testing."""

    # Create a mock path.join function
    def path_join(*parts, sep="/"):
        clean_parts = []
        for part in parts:
            if part:  # Skip empty parts
                # Convert to string and remove leading/trailing separators
                part_str = str(part).strip(sep)
                if part_str:  # Only add if there's something left
                    clean_parts.append(part_str)
        return sep.join(clean_parts)

    # Create a mock makedirs function
    def mock_makedirs(path, exist_ok=False):
        return True

    # Create a mock path.exists function that returns True by default
    def mock_exists(path):
        return True

    with smart_mock(
        "os",
        **{
            "path.exists": mock_exists,  # Use our callable mock_exists function
            "environ": {"TEST_VAR": "test_value", "LOG_CONFIG_FILE": "logging_config.ini"},
            "path.join": path_join,  # Use our custom path_join function
            "makedirs": mock_makedirs,  # Use our custom makedirs function
        }
    ) as mock_ctx:
        yield mock_ctx


@pytest.fixture
def mock_builtins():
    # Create a mock file object with close method
    mock_file = Mock()
    mock_file.close = Mock()

    # Create a mock open function that returns the mock file
    mock_open = Mock(return_value=mock_file)

    with smart_mock(
        "builtins",
        open=mock_open,
        print=Mock(),
    ) as mock_ctx:
        yield mock_ctx


@pytest.fixture
def mock_logging():
    """Fixture to mock logging setup."""
    mock_fileconfig = Mock()
    with smart_mock(
        "logging",
        getLogger=Mock(),
        **{"config.fileConfig": mock_fileconfig}
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
    # Create a mock for get_init that returns True
    def get_init_mock():
        return True

    # Use smart_mock to automatically detect the best mocking strategy
    with smart_mock(
        "pygame.mixer",
        init=Mock(),
        get_init=get_init_mock,  # Use our mock function that returns True
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


@pytest.fixture(autouse=True)
def mock_dotenv():
    """Mock dotenv.load_dotenv to prevent actual file loading."""
    # Create a callable mock for load_dotenv that returns True
    mock_load_dotenv = Mock(return_value=True)

    # Directly patch the renamed function in the env_checks module
    with patch('src.utils.env_checks.env_checks.dotenv_load_dotenv', mock_load_dotenv):
        yield mock_load_dotenv
