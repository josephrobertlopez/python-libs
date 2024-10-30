import os
import argparse
import time
from src.utils.audio import play_alarm_sound
from src.utils.environment import get_env_var


def main(*args) -> None:
    """
    Set a Pomodoro timer for a given number of minutes.

    The expected argument is:
    - --minutes: Set the Pomodoro timer for this many minutes.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--minutes", type=int, required=True,
                        help="Set the Pomodoro timer for this many minutes.")
    parsed_args = parser.parse_args(args)  # Parse the arguments passed from run.py

    minutes = parsed_args.minutes
    if minutes < 0:
        print("Minutes must be a natural number.")
        return

    seconds = minutes * 60
    print(f"Pomodoro timer set for {minutes} minutes.")
    time.sleep(seconds)

    SOUND_FILE = get_env_var("SOUND_FILE")

    play_alarm_sound(SOUND_FILE)
