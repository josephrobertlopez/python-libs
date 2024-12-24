import pygame
import time
from src.utils.abstract.abstract_singleton import AbstractSingleton


class PygameMixerAudio(AbstractSingleton):

    def __init__(self):
        if not self.test_initialization():
            raise Exception("More than one singleton attempted to be created")
        self.setup()

    def setup(self) -> None:
        """Initialize the pygame mixer and check for successful initialization."""
        pygame.mixer.init()
        if not pygame.mixer.get_init():
            raise RuntimeError(
                "Mixer not initialized. "
                "Ensure that your audio subsystem is set up correctly."
            )

    @staticmethod
    def play_alarm_sound(sound_file: str) -> None:
        """Play an alarm sound from the provided file.

        Args:
            sound_file (str): The path to the sound file to play.

        Raises:
            RuntimeError: If the mixer is not initialized or
            if there is an error playing the sound.
        """
        try:
            alarm_sound = pygame.mixer.Sound(sound_file)
            alarm_sound.play()

            while pygame.mixer.get_busy():
                time.sleep(0.1)
            print("Alarm sound played successfully.")
        except pygame.error as e:
            raise RuntimeError(f"Error playing sound: {e}")

    @staticmethod
    def is_sound_playing() -> bool:
        """Check if background sound is currently playing.

        Returns:
            bool: True if music is playing, False otherwise.
        """
        if pygame.mixer.music.get_busy():
            return True
        return False

    @staticmethod
    def toggle_sound_on_or_off() -> None:
        """Play or pause sound."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

    @staticmethod
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

    @staticmethod
    def play_on_loop(sound_file: str) -> None:
        """Play background music from the provided file in a loop.

        Args:
            sound_file (str): The path to the sound file to load.

        Raises:
            RuntimeError: If there is an error playing the music.
        """
        try:
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play(-1)  # Loop indefinitely
        except pygame.error as e:
            raise RuntimeError(f"Error playing music: {e}")

    @staticmethod
    def load_sound(sound_file: str) -> None:
        """Load a sound file.

        Args:
            sound_file (str): The path to the sound file to load.

        Raises:
            RuntimeError: If there is an error loading the sound.
        """
        try:
            pygame.mixer.Sound(sound_file)
        except pygame.error as e:
            raise RuntimeError(f"Error loading sound: {e}")
