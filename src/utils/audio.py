import pygame
import time
from src.utils.environment import get_resource_path


def initialize_pygame_mixer() -> None:
    """Initialize the pygame mixer and check for successful initialization."""
    pygame.mixer.init()
    if not pygame.mixer.get_init():
        raise RuntimeError("Mixer not initialized. Ensure that your audio subsystem is set up correctly.")


def play_alarm_sound(sound_file: str) -> None:
    """Play an alarm sound from the provided file.

    Args:
        sound_file (str): The path to the sound file to play.
    
    Raises:
        RuntimeError: If the mixer is not initialized or if there is an error playing the sound.
    """
    initialize_pygame_mixer()

    resource_path = get_resource_path(sound_file)

    try:
        alarm_sound = pygame.mixer.Sound(resource_path)
        alarm_sound.play()

        while pygame.mixer.get_busy():
            time.sleep(0.1)
        print("Alarm sound played successfully.")
    except pygame.error as e:
        raise RuntimeError(f"Error playing sound: {e}")


def is_music_playing() -> bool:
    """Check if background music is currently playing.

    Returns:
        bool: True if music is playing, False otherwise.
    """
    if pygame.mixer.music.get_busy():
        return True
    return False


def unpause_background_music() -> None:
    """Unpause previously paused background music."""
    if not pygame.mixer.music.get_busy():
        raise RuntimeError("No music is currently paused.")
    pygame.mixer.music.unpause()


def pause_background_music() -> None:
    """Pause currently playing background music."""
    pygame.mixer.music.pause()


def set_volume(volume: float) -> None:
    """Set the volume for the mixer.

    Args:
        volume (float): Volume level between 0.0 (mute) and 1.0 (max).
    
    Raises:
        ValueError: If volume is out of range.
    """
    if not (0.0 <= volume <= 1.0):
        raise ValueError("Volume must be between 0.0 and 1.0.")

    pygame.mixer.music.set_volume(volume)  # Set volume for music


def play_background_music(music_file: str) -> None:
    """Play background music from the provided file in a loop.

    Args:
        music_file (str): The path to the music file to play.
    
    Raises:
        RuntimeError: If there is an error playing the music.
    """
    resource_path = get_resource_path(music_file)

    try:
        pygame.mixer.music.load(resource_path)
        pygame.mixer.music.play(-1)  # Loop indefinitely
    except pygame.error as e:
        raise RuntimeError(f"Error playing music: {e}")


def load_sound(sound_file: str) -> None:
    """Load a sound file.

    Args:
        sound_file (str): The path to the sound file to load.
    
    Raises:
        RuntimeError: If there is an error loading the sound.
    """
    resource_path = get_resource_path(sound_file)

    try:
        pygame.mixer.Sound(resource_path)
    except pygame.error as e:
        raise RuntimeError(f"Error loading sound: {e}")
