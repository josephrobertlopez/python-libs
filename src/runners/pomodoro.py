import time

from src.utils.abstract.abstract_runner import AbstractRunner
from src.utils.env_checks.env_checks import get_path_based_env_var
from src.utils.media.audio import PygameMixerSoundSingleton


class PomodoroRunner(AbstractRunner):
    """Concrete implementation of the Pomodoro runner."""

    def __init__(self):
        """Initialize the Pomodoro runner."""
        super().__init__()

    @property
    def argument_definitions(self):
        """Argument definitions for the Pomodoro timer."""
        return {
            "-m": {
                "help": "Set the Pomodoro timer for this many minutes.",
                "type": int,
                "dest": "minutes",
            },
            "--minutes": {
                "help": "Set the Pomodoro timer for this many minutes.",
                "type": int,
                "dest": "minutes",
            },
        }

    def main(self, *args) -> None:
        """
        Set a Pomodoro timer for a given number of minutes.

        The expected argument is:
        - --minutes or -m: Set the Pomodoro timer for this many minutes.
        """
        self.initialized_arguments(*args)
        # Ensure we have the minutes argument
        if self.parsed_args.minutes is None:
            raise ValueError(
                "You must specify the Pomodoro timer duration using --minutes or -m."
            )

        minutes = self.parsed_args.minutes
        if minutes < 0:
            raise ValueError("Minutes must be a natural number.")

        seconds = minutes * 60
        print(f"Pomodoro timer set for {minutes} minutes.")

        # Wait for the Pomodoro timer to expire
        time.sleep(seconds)

        # Get the sound file path from the environment variable
        SOUND_FILE = get_path_based_env_var("SOUND_FILE")

        # Initialize and play the alarm sound
        audio_player = PygameMixerSoundSingleton()
        audio_player.load_sound(SOUND_FILE)
        audio_player.play_sound()

        if not audio_player.is_sound_playing():
            print("Alarm sound played successfully.")
            print("Pomodoro session complete. Time to take a break!")
