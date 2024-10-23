import pygame
import sys
import time
from src.utils.environment import get_resource_path

def play_alarm_sound(sound_file: str) -> tuple:
    """Play an alarm sound from the provided file.

    Args:
        sound_file (str): The path to the sound file to play.

    Returns:
        tuple: (bool, str) indicating success or failure and an accompanying message.
    """
    pygame.mixer.init()
    if not pygame.mixer.get_init():
        return False, "Mixer not initialized."

    # Attempt to load the sound file
    success, resource_path = get_resource_path(sound_file)
    if not success:
        return False,resource_path  # Return error if sound file is not found

    try:
        alarm_sound = pygame.mixer.Sound(resource_path)
        alarm_sound.play()

        while pygame.mixer.get_busy():
            time.sleep(0.1)
    except pygame.error as e:
        return False, f"Error playing sound: {e}"

    pygame.mixer.quit()
    return True, "Alarm sound played successfully."

def is_music_playing() -> tuple:
    """Check if background music is currently playing.

    Returns:
        tuple: (bool, str) indicating whether music is playing and an accompanying message.
    """
    if pygame.mixer.music.get_busy():
        return True, "Background music is currently playing."
    else:
        return False, "No background music is playing."


def unpause_background_music() -> tuple:
    """Unpause previously paused background music.

    Returns:
        tuple: (bool, str) indicating success or failure and an accompanying message.
    """
    pygame.mixer.music.unpause()
    return True, "Background music unpaused."


def pause_background_music() -> tuple:
    """Pause currently playing background music.

    Returns:
        tuple: (bool, str) indicating success or failure and an accompanying message.
    """
    pygame.mixer.music.pause()
    return True, "Background music paused."

def set_volume(volume: float) -> tuple:
    """Set the volume for the mixer.

    Args:
        volume (float): Volume level between 0.0 (mute) and 1.0 (max).

    Returns:
        tuple: (bool, str) indicating success or failure and an accompanying message.
    """
    if not (0.0 <= volume <= 1.0):
        return False, "Volume must be between 0.0 and 1.0."

    pygame.mixer.music.set_volume(volume)  # Set volume for music
    return True, f"Volume set to {volume}."

def set_volume(volume: float) -> tuple:
    """Set the volume for the mixer.

    Args:
        volume (float): Volume level between 0.0 (mute) and 1.0 (max).

    Returns:
        tuple: (bool, str) indicating success or failure and an accompanying message.
    """
    if not (0.0 <= volume <= 1.0):
        return False, "Volume must be between 0.0 and 1.0."

    pygame.mixer.music.set_volume(volume)  # Set volume for music
    return True, f"Volume set to {volume}."

def play_background_music(music_file: str) -> tuple:
    """Play background music from the provided file in a loop.

    Args:
        music_file (str): The path to the music file to play.

    Returns:
        tuple: (bool, str) indicating success or failure and an accompanying message.
    """
    success, resource_path = get_resource_path(music_file)
    if not success:
        return False, resource_path  # Return error if music file is not found

    try:
        pygame.mixer.music.load(resource_path)
        pygame.mixer.music.play(-1)  # Loop indefinitely
        return True, "Background music started playing."
    except pygame.error as e:
        return False, f"Error playing music: {e}"


def load_sound(sound_file: str) -> tuple:
    """Load a sound file.

    Args:
        sound_file (str): The path to the sound file to load.

    Returns:
        tuple: (bool, pygame.mixer.Sound or str) indicating success or failure and the sound object or error message.
    """
    success, resource_path = get_resource_path(sound_file)
    if not success:
        return False, resource_path  # Return error if sound file is not found

    try:
        sound = pygame.mixer.Sound(resource_path)
        return True, sound
    except pygame.error as e:
        return False, f"Error loading sound: {e}"
