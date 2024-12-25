import pygame
import pytest
from unittest.mock import patch, MagicMock
from src.utils.abstract.abstract_singleton import AbstractSingleton
from src.utils.media.audio import PygameMixerAudio


@pytest.fixture
def pygame_mixer_audio():
    """Fixture to instantiate the PygameMixerAudio singleton."""
    audio_instance = PygameMixerAudio()
    return audio_instance


def test_singleton_creation(pygame_mixer_audio):
    """Test that only one instance of PygameMixerAudio can be created."""
    second_mixer = PygameMixerAudio()
    assert second_mixer == pygame_mixer_audio


def test_setup_called_once(pygame_mixer_audio):
    """Test that setup can only be called once."""
    # We will patch the actual pygame mixer init to prevent real initialization
    with patch('pygame.mixer',return_value = True) as mock_init:
        pygame_mixer_audio.setup()  # First call should work
        mock_init.init.assert_called_once()

        with pytest.raises(RuntimeError, match="setup() has already been called"):
            pygame_mixer_audio.setup()  # Second call should raise an error
            pygame_mixer_audio.setup()


def test_delete_and_reinstantiate_singleton():
    """Test that deleting and re-instantiating the singleton works."""
    # First, create the instance
    audio_instance_1 = PygameMixerAudio()

    # Ensure the instance is created
    assert audio_instance_1 is not None
    assert PygameMixerAudio.test_initialization() is True  # Check that the instance is initialized

    # Delete the instance
    PygameMixerAudio.delete_instance()

    # Ensure the instance was deleted
    assert PygameMixerAudio.test_initialization() is False  # Ensure the instance is deleted

    # Recreate the instance after deletion
    audio_instance_2 = PygameMixerAudio()

    # Ensure the new instance is the same type and is created
    assert isinstance(audio_instance_2, PygameMixerAudio)
    assert audio_instance_1 is not audio_instance_2  # The two instances should be different, but both are valid singletons

