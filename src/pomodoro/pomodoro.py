import argparse
import time

from src.utils.abstract.abstract_runner import AbstractRunner
from src.utils.env_checks.env_checks import get_env_var
from src.utils.media.audio import PygameMixerAudioSingleton


class PomodoroRunner(AbstractRunner):
    """Concrete implementation of the Pomodoro runner."""

    def __init__(self):
        """Initialize the Pomodoro runner."""
        super().__init__()

    def main(self, *args) -> None:
        """
        Set a Pomodoro timer for a given number of minutes.

        The expected argument is:
        - --minutes or -m: Set the Pomodoro timer for this many minutes.
        """
        # Define the arguments for the Pomodoro timer
        parser = argparse.ArgumentParser()
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "-m",
            "--minutes",
            type=int,
            help="Set the Pomodoro timer for this many minutes.",
        )

        # Parse the arguments
        parsed_args = parser.parse_args(args)

        minutes = parsed_args.minutes
        if minutes < 0:
            raise ValueError("Minutes must be a natural number.")

        seconds = minutes * 60
        print(f"Pomodoro timer set for {minutes} minutes.")

        # Wait for the Pomodoro timer to expire
        time.sleep(seconds)

        # Get the sound file path from the environment variable
        SOUND_FILE = get_env_var("SOUND_FILE")

        # Initialize and play the alarm sound
        audio_player = PygameMixerAudioSingleton()
        audio_player.play_alarm_sound(SOUND_FILE)
        print("Pomodoro session complete. Time to take a break!")


# Example of how to run the Pomodoro timer
if __name__ == "__main__":
    runner = PomodoroRunner()
    runner.main("-m", "25")  # Example: 25-minute Pomodoro timer
    # Alternatively, you can use --minutes:
    # runner.main("--minutes", "25")
