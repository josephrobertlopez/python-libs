from unittest.mock import MagicMock, patch

import pygame
from src.utils.abstract.abstract_singleton import AbstractSingleton
from src.utils.test.MockContextManager import MockContextManager
from src.utils.media.audio import PygameMixerAudioSingleton
import pytest


@pytest.fixture(autouse=True)
def mock_singleton_setup():
    """Fixture to mock AbstractSingleton setup and ensure it's called only once."""
    # Patch the setup method in AbstractSingleton to prevent the singleton check
    with patch.object(AbstractSingleton, "setup", MagicMock()) as mock_setup:
        # Ensure the singleton is set up before each test
        mock_setup()
        yield mock_setup
        # After each test, delete the setup to ensure it does not interfere with other tests
        del mock_setup


@pytest.fixture
def pygame_mixer_audio():
    """Fixture to provide a PygameMixerAudio instance with mocked dependencies."""
    # Set up the mock behaviors for methods you want to mock
    method_behaviors = {
        "init": MagicMock(),
        "music.get_busy": False,
        "music.play": MagicMock(),
        "music.pause": MagicMock(),
        "Sound": MagicMock(),
    }
    manager = MockContextManager(
        target_path="pygame.mixer",
        method_behaviors=method_behaviors,
    )
    return manager


@pytest.fixture
def mixer(pygame_mixer_audio):
    """Fixture to initialize PygameMixerAudio instance."""
    # Initialize PygameMixerAudio instance before each test
    mixer = PygameMixerAudioSingleton()
    # Ensure the singleton is set up in the context
    with pygame_mixer_audio:
        yield mixer


# Define the behavior for the mock sound to simulate an error
def raise_pygame_error(*args, **kwargs):
    raise pygame.error("Sound error")


def test_play_alarm_sound(mixer, pygame_mixer_audio):
    # Mocking the pygame.mixer.Sound class to simulate successful sound playback
    with pygame_mixer_audio:
        # Run the play_alarm_sound method
        mixer.play_alarm_sound("alarm.wav")

        # Assert that the play method was called once
        pygame_mixer_audio.get_mock("Sound")().play.assert_called_once()

    with pygame_mixer_audio.update_patch("Sound", raise_pygame_error):
        with pytest.raises(RuntimeError, match="Error playing sound: Sound error"):
            mixer.play_alarm_sound("alarm.wav")


def test_is_sound_playing(mixer, pygame_mixer_audio):
    """Test that is_sound_playing returns True when sound is playing."""
    with pygame_mixer_audio:
        assert not mixer.is_sound_playing()
    with pygame_mixer_audio.update_patch("music.get_busy", True):
        assert mixer.is_sound_playing()


def test_toggle_sound(mixer, pygame_mixer_audio):

    # with pygame_mixer_audio.update_patch("music.get_busy",True):
    #     mixer.toggle_sound()
    #     pygame_mixer_audio.get_mock("music.play").assert_not_called()
    #     pygame_mixer_audio.get_mock("music.pause").assert_called_once()
    #

    with pygame_mixer_audio:
        mixer.toggle_sound()
        pygame_mixer_audio.get_mock("music.play").assert_called_once()
        pygame_mixer_audio.get_mock("music.pause").assert_not_called()
    with pygame_mixer_audio:
        mixer.toggle_sound()
        pygame_mixer_audio.get_mock("music.play").assert_called_once()
        pygame_mixer_audio.get_mock("music.pause").assert_not_called()


#
# def test_toggle_sound_on_or_off_play(pygame_mixer_audio):
#     """Test the toggle_sound_on_or_off method when the sound is paused."""
#     manager = MockContextManager(
#         target_path="pygame.mixer.music",
#         method_behaviors={"get_busy": MagicMock(return_value=False), "play": MagicMock()},
#     )
#     with manager:
#         pygame_mixer_audio.toggle_sound_on_or_off()  # Should call play
#         manager.get_mock("play").assert_called_once()
#
#
# def test_toggle_sound_on_or_off_pause(pygame_mixer_audio):
#     """Test the toggle_sound_on_or_off method when sound is playing."""
#     manager = MockContextManager(
#         target_path="pygame.mixer.music",
#         method_behaviors={"get_busy": MagicMock(return_value=True), "pause": MagicMock()},
#     )
#     with manager:
#         pygame_mixer_audio.toggle_sound_on_or_off()  # Should call pause
#         manager.get_mock("pause").assert_called_once()
#
#
# def test_set_volume_success(pygame_mixer_audio):
#     """Test that the volume is set correctly."""
#     manager = MockContextManager(
#         target_path="pygame.mixer.music",
#         method_behaviors={"set_volume": MagicMock()},
#     )
#     with manager:
#         pygame_mixer_audio.set_volume(0.5)
#         manager.get_mock("set_volume").assert_called_once_with(0.5)
#
#
# def test_set_volume_failure(pygame_mixer_audio):
#     """Test that an error is raised when setting an invalid volume."""
#     with pytest.raises(ValueError, match="Volume must be between 0.0 and 1.0"):
#         pygame_mixer_audio.set_volume(1.5)
#
#
# def test_play_on_loop(pygame_mixer_audio):
#     """Test that the music is played in a loop."""
#     manager = MockContextManager(
#         target_path="pygame.mixer.music",
#         method_behaviors={"load": MagicMock(), "play": MagicMock()},
#     )
#     with manager:
#         pygame_mixer_audio.play_on_loop("loop.wav")
#         manager.get_mock("load").assert_called_once_with("loop.wav")
#         manager.get_mock("play").assert_called_once_with(-1)
#
#
# def test_load_sound_success(pygame_mixer_audio):
#     """Test that the sound file is loaded successfully."""
#     manager = MockContextManager(
#         target_path="pygame.mixer", method_behaviors={"Sound": MagicMock()}
#     )
#     with manager:
#         pygame_mixer_audio.load_sound("sound.wav")
#         manager.get_mock("Sound").assert_called_once_with("sound.wav")
#
#
# def test_load_sound_failure(pygame_mixer_audio):
#     """Test that an error is raised when loading a sound file fails."""
#     manager = MockContextManager(
#         target_path="pygame.mixer",
#         method_behaviors={"Sound": MagicMock(side_effect=pygame_error("Sound error"))},
#     )
#     with manager:
#         with pytest.raises(RuntimeError, match="Error loading sound: Sound error"):
#             pygame_mixer_audio.load_sound("sound.wav")
