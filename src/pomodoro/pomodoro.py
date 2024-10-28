import os
import argparse
import time
import logging
from src.utils.audio import play_alarm_sound  # Adjusted import to reflect package structure
from src.utils.logging_setup import setup_logging  # Import logging setup before anything else


def main() -> None:
    """
    Set a Pomodoro timer for a given number of minutes.

    Command line arguments:

    -m, --minutes: Set the Pomodoro timer for this many minutes. Must be a positive integer.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--minutes", type=int, required=True,
                        help="Set the Pomodoro timer for this many minutes.")
    args = parser.parse_args()

    minutes: int = args.minutes
    seconds: int = minutes * 60
    logging.info(f"Pomodoro timer set for {minutes} minutes.")
    time.sleep(seconds)
    sound_file = os.path.join("resources", "sounds", "alarm_sound.wav")

    play_alarm_sound(sound_file)


if __name__ == "__main__":
    setup_logging()
    main()
