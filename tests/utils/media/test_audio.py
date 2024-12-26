import pygame

from src.utils.abstract.abstract_singleton import AbstractSingleton
from src.utils.test.MockContextManager import MockContextManager
from src.utils.test.MockPatchingStrategies import (
    AttributePatcherStrategy,
    MappingPatcherStrategy,
    MethodPatcherStrategy,
)
from src.utils.media.audio import PygameMixerAudioSingleton
import pytest
from pygame import error as pygame_error
from unittest.mock import MagicMock, patch, Mock

import pygame
from src.utils.abstract.abstract_singleton import AbstractSingleton
from src.utils.test.MockContextManager import MockContextManager
from src.utils.test.MockPatchingStrategies import (
    AttributePatcherStrategy,
    MappingPatcherStrategy,
    MethodPatcherStrategy,
)
from src.utils.media.audio import PygameMixerAudioSingleton
import pytest
from pygame import error as pygame_error
from unittest.mock import MagicMock, patch, Mock


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
        "music.get_busy": MagicMock(return_value=False),
        "music.play": MagicMock(),
        "music.pause": MagicMock(),
        "music.set_volume": MagicMock(),
    }

    # Using MockContextManager to patch pygame.mixer.Sound (actual class)
    manager = MockContextManager(
        target_path="pygame.mixer",
        method_behaviors=method_behaviors,
        class_values={"Sound": pygame.mixer.Sound}  # Pass the actual class
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

def test_play_alarm_sound_success(mixer, pygame_mixer_audio):
    """Test that the alarm sound is played successfully."""
    with pygame_mixer_audio:
        # Call the method that plays the sound
        mixer.play_alarm_sound("alarm.wav")
        # Get the mock for pygame.mixer.Sound and assert it was called correctly
        sound_mock = pygame_mixer_audio.get_mock("Sound")
        sound_mock.assert_called_with("alarm.wav")
        # Ensure the play method was called once
        sound_mock.return_value.play.assert_called_once()

#
#
# def test_play_alarm_sound_failure(pygame_mixer_audio):
#     """Test that an error is raised when playing the alarm sound fails."""
#     manager = MockContextManager(
#         target_path="pygame.mixer",
#         method_behaviors={"Sound": MagicMock(side_effect=pygame_error("Sound error"))},
#     )
#     with manager:
#         with pytest.raises(RuntimeError, match="Error playing sound: Sound error"):
#             pygame_mixer_audio.play_alarm_sound("alarm.wav")
#
#
# def test_is_sound_playing_true(pygame_mixer_audio):
#     """Test that is_sound_playing returns True when sound is playing."""
#     manager = MockContextManager(
#         target_path="pygame.mixer.music", method_behaviors={"get_busy": MagicMock(return_value=True)}
#     )
#     with manager:
#         assert pygame_mixer_audio.is_sound_playing() is True
#
#
# def test_is_sound_playing_false(pygame_mixer_audio):
#     """Test that is_sound_playing returns False when no sound is playing."""
#     manager = MockContextManager(
#         target_path="pygame.mixer.music", method_behaviors={"get_busy": MagicMock(return_value=False)}
#     )
#     with manager:
#         assert pygame_mixer_audio.is_sound_playing() is False
#
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
