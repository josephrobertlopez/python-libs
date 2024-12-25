import pygame
import pytest
from unittest.mock import patch, MagicMock
from src.utils.media.audio import PygameMixerAudio
from src.utils.abstract.abstract_singleton import AbstractSingleton


@pytest.fixture(autouse=True)
def mock_singleton_setup():
    """Fixture to mock AbstractSingleton setup and ensure it's called only once."""
    # Patch the setup method in AbstractSingleton to prevent the singleton check
    with patch.object(AbstractSingleton, 'setup', MagicMock()) as mock_setup:
        yield mock_setup
        # After each test, delete the setup to ensure it does not interfere with other tests
        del mock_setup


@pytest.fixture
def pygame_mixer_audio():
    """Fixture to mock pygame.mixer and initialize PygameMixerAudio."""
    with patch("pygame.mixer.init") as mock_init, \
         patch("pygame.mixer.music") as mock_music, \
         patch("pygame.mixer.Sound") as mock_sound:
        mock_init.return_value = None  # Mock the pygame.mixer initialization
        mock_music.get_busy.return_value = False  # Simulate no music playing
        mock_sound.return_value.play = MagicMock()  # Mock the play method for sounds
        yield PygameMixerAudio()  # Return the PygameMixerAudio instance


def test_play_alarm_sound_success(pygame_mixer_audio):
    """Test that the alarm sound is played successfully."""
    with patch("pygame.mixer.Sound") as mock_sound:
        mock_sound.return_value.play = MagicMock()

        pygame_mixer_audio.play_alarm_sound("alarm.wav")
        mock_sound.assert_called_once_with("alarm.wav")
        mock_sound.return_value.play.assert_called_once()


def test_play_alarm_sound_failure(pygame_mixer_audio):
    """Test that an error is raised when playing the alarm sound fails."""
    with patch("pygame.mixer.Sound") as mock_sound:
        mock_sound.side_effect = pygame.error("Sound error")

        with pytest.raises(RuntimeError, match="Error playing sound: Sound error"):
            pygame_mixer_audio.play_alarm_sound("alarm.wav")


def test_is_sound_playing_true(pygame_mixer_audio):
    """Test that is_sound_playing returns True when sound is playing."""
    with patch("pygame.mixer.music.get_busy", return_value=True):
        assert pygame_mixer_audio.is_sound_playing() is True


def test_is_sound_playing_false(pygame_mixer_audio):
    """Test that is_sound_playing returns False when no sound is playing."""
    with patch("pygame.mixer.music.get_busy", return_value=False):
        assert pygame_mixer_audio.is_sound_playing() is False


def test_toggle_sound_on_or_off_play(pygame_mixer_audio):
    """Test the toggle_sound_on_or_off method when the sound is paused."""
    with patch("pygame.mixer.music.get_busy", return_value=False):
        with patch("pygame.mixer.music.play") as mock_play:
            pygame_mixer_audio.toggle_sound_on_or_off()  # Should call play
            mock_play.assert_called_once()


def test_toggle_sound_on_or_off_pause(pygame_mixer_audio):
    """Test the toggle_sound_on_or_off method when sound is playing."""
    with patch("pygame.mixer.music.get_busy", return_value=True):
        with patch("pygame.mixer.music.pause") as mock_pause:
            pygame_mixer_audio.toggle_sound_on_or_off()  # Should call pause
            mock_pause.assert_called_once()


def test_set_volume_success(pygame_mixer_audio):
    """Test that the volume is set correctly."""
    with patch("pygame.mixer.music.set_volume") as mock_set_volume:
        pygame_mixer_audio.set_volume(0.5)
        mock_set_volume.assert_called_once_with(0.5)


def test_set_volume_failure(pygame_mixer_audio):
    """Test that an error is raised when setting an invalid volume."""
    with pytest.raises(ValueError, match="Volume must be between 0.0 and 1.0"):
        pygame_mixer_audio.set_volume(1.5)


def test_play_on_loop(pygame_mixer_audio):
    """Test that the music is played in a loop."""
    with patch("pygame.mixer.music.load") as mock_load, patch(
        "pygame.mixer.music.play"
    ) as mock_play:
        pygame_mixer_audio.play_on_loop("loop.wav")
        mock_load.assert_called_once_with("loop.wav")
        mock_play.assert_called_once_with(-1)


def test_load_sound_success(pygame_mixer_audio):
    """Test that the sound file is loaded successfully."""
    with patch("pygame.mixer.Sound") as mock_sound:
        pygame_mixer_audio.load_sound("sound.wav")
        mock_sound.assert_called_once_with("sound.wav")


def test_load_sound_failure(pygame_mixer_audio):
    """Test that an error is raised when loading a sound file fails."""
    with patch("pygame.mixer.Sound") as mock_sound:
        mock_sound.side_effect = pygame.error("Sound error")

        with pytest.raises(RuntimeError, match="Error loading sound: Sound error"):
            pygame_mixer_audio.load_sound("sound.wav")
