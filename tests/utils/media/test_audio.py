from unittest.mock import patch, Mock
from src.utils.abstract.abstract_singleton import AbstractSingleton
from src.utils.test.MockContextManager import MockContextManager
from src.utils.media.audio import PygameMixerSoundSingleton
import pytest


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


@pytest.fixture(autouse=True)
def mock_singleton_setup():
    """Fixture to mock AbstractSingleton setup and ensure it's called only once."""
    # Patch the setup method in AbstractSingleton to prevent the singleton check
    with patch.object(AbstractSingleton, "setup", Mock()) as mock_setup:
        # Ensure the singleton is set up before each test
        mock_setup()
        yield mock_setup
        # After each test, delete the setup to ensure it does not interfere with other tests
        del mock_setup


def test_load_sound(mixer, pygame_mixer_audio):
    with pygame_mixer_audio:
        mixer.load_sound("Fake_sound.wav")
        pygame_mixer_audio.get_mock("Sound").assert_called_once()
    with pygame_mixer_audio.remove_patch("Sound") as m:
        del m
        mixer.load_sound("Fake_sound.wav")


def test_play_alarm_sound(mixer, pygame_mixer_audio):
    # Mocking the pygame.mixer.Sound class to simulate successful sound playback
    with pygame_mixer_audio:
        # Run the play_alarm_sound method
        # Assert that the play method was called once
        mixer.load_sound("Fake_sound.wav")
        mixer.play_sound()
        pygame_mixer_audio.get_mock("Sound")().play.assert_called_once()


def test_is_sound_playing(mixer, pygame_mixer_audio):
    """Test that is_sound_playing returns True when sound is playing."""
    with pygame_mixer_audio:
        assert not mixer.is_sound_playing()
        mixer.load_sound("Fake_sound.wav")
        assert mixer.is_sound_playing()
