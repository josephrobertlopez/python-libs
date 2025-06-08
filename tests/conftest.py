import pytest
import os
from unittest.mock import Mock, patch
from src.utils.abstract.abstract_runner import SampleConcreteRunner
from src.utils.abstract.abstract_singleton import (
    AbstractSingleton,
    SampleConcreteSingleton,
)
from src.utils.media.audio import PygameMixerSoundSingleton
from src.utils.test import smart_mock, quick_mock, runtime_context
from .shared_annotations import (
    mock_test_sys,
    mock_test_os,
    mock_test_builtins,
    mock_test_logging,
    mock_test_pygame,
    mock_runner_context,
    mock_audio_context,
    mock_logging_context,
)


# =============================================================================
# LEGACY FIXTURES (for backward compatibility)
# =============================================================================


@pytest.fixture
def mock_sys():
    """Legacy fixture - use @mock_test_sys decorator instead."""
    with mock_test_sys():
        yield


@pytest.fixture
def mock_os():
    """Legacy fixture - use @mock_test_os decorator instead."""
    with mock_test_os():
        yield


@pytest.fixture
def mock_builtins():
    """Legacy fixture - use @mock_test_builtins decorator instead."""
    with mock_test_builtins():
        yield


@pytest.fixture
def mock_logging():
    """Legacy fixture - use @mock_test_logging decorator instead."""
    with mock_test_logging():
        yield


# =============================================================================
# ENHANCED CONTEXT FIXTURES (recommended approach)
# =============================================================================


@pytest.fixture
def runner_context():
    """Context manager for runner tests with standard configuration."""
    return mock_runner_context


@pytest.fixture
def audio_context():
    """Context manager for audio tests with pygame mocking."""
    return mock_audio_context


@pytest.fixture
def logging_context():
    """Context manager for logging tests."""
    return mock_logging_context


# =============================================================================
# DOMAIN-SPECIFIC FIXTURES
# =============================================================================


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
    """Enhanced pygame mixer fixture using shared annotations."""
    from src.utils.test import runtime_context

    with runtime_context("audio_system"):
        yield


@pytest.fixture
def mixer(pygame_mixer_audio):
    """Fixture to initialize PygameMixerAudio instance."""
    mixer = PygameMixerSoundSingleton()
    yield mixer


@pytest.fixture()
def mock_singleton_setup():
    """Fixture to mock AbstractSingleton setup and ensure it's called only once."""
    with patch_object(AbstractSingleton, "setup", Mock()) as mock_setup:
        mock_setup()
        yield mock_setup
        del mock_setup


# =============================================================================
# AUTO-USE FIXTURES (global test environment)
# =============================================================================


@pytest.fixture(autouse=True)
def setup_headless_audio():
    """Set up the headless audio environment for Pygame in CI."""
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    yield
    del os.environ["SDL_AUDIODRIVER"]


@pytest.fixture(autouse=True)
def mock_dotenv():
    """Mock dotenv.load_dotenv to prevent actual file loading."""
    mock_load_dotenv = Mock(return_value=True)
    with patch("src.utils.env_checks.env_checks.dotenv_load_dotenv", mock_load_dotenv):
        yield mock_load_dotenv


# =============================================================================
# LEGACY COMPATIBILITY FIXTURE
# =============================================================================


@pytest.fixture
def mock_context():
    """Legacy fixture for backward compatibility."""
    return {
        "target_path": "tests.utils.test.test_mockcontextmanager",
        "method_behaviors": {"method_name": lambda x: x * 2},
        "attribute_values": {"attr_name": 42},
        "mapping_values": {"map_name": {"key": "value"}},
    }
