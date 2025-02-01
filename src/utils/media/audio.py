import pygame
import time

from src.utils.abstract.abstract_singleton import AbstractSingleton


class PygameMixerSoundSingleton(AbstractSingleton):

    def __init__(self):
        self._sound = None
        if not self.test_initialization():
            raise Exception("More than one singleton attempted to be created")
        self.setup()

    def _setup(self) -> None:
        """Initialize the pygame mixer and check for successful initialization."""
        pygame.mixer.init()
        if not pygame.mixer.get_init():
            raise RuntimeError(
                "Mixer not initialized. "
                "Ensure that your audio subsystem is set up correctly."
            )

    def load_sound(self, sound_file: str) -> None:
        """Load a sound file.

        Args:
            sound_file (str): The path to the sound file to load.

        Raises:
            RuntimeError: If there is an error loading the sound.
        """
        self._sound = pygame.mixer.Sound(sound_file)

    def play_sound(self, until_time: int = None):
        self._sound.play()
        if until_time:
            time.sleep(until_time)
            print(f"slept for seconds: {until_time}")
            return
        while pygame.mixer.get_busy():
            time.sleep(0.1)

    def is_sound_playing(self) -> bool:
        """Check if background sound is currently playing.

        Returns:
            bool: True if music is playing, False otherwise.
        """
        if not self._sound:
            return False
        return self._sound.get_num_channels() > 0
