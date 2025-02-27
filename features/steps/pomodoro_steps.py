import os
import time
from unittest import mock

from behave import given, when, then


@given("I have set the Pomodoro timer for {minutes} minute(s)")
def step_impl_set_timer(context, minutes):
    context.minutes = int(minutes)


@given("I have not provided any timer arguments")
def step_impl_no_arguments(context):
    context.minutes = ""


@when("the timer starts")
def step_impl_start_timer(context):
    with mock.patch("src.utils.media.audio.PygameMixerSoundSingleton.play_sound"):
        try:
            # Start the timer process with additional context
            context.app.run("pomodoro", ["--minutes", context.minutes])
        except Exception as e:
            context.error = e


@then("I should hear an alarm sound after {minutes:d} minute(s)")
def step_impl_hear_alarm(context, minutes):
    # Wait for the specified minutes (use `time.sleep` to simulate the waiting
    # period)
    time.sleep(minutes * 60)  # Adjust to full minutes instead of 59 seconds

    # Check the contents of the log file for the alarm message
    log_file_path = "resources/logs/app.log"

    # Check if the log file exists before reading
    assert os.path.exists(log_file_path), "Log file does not exist."

    # Read the log file
    with open(log_file_path, "r") as log_file:
        log_contents = log_file.read()

    # Check if the alarm sound played successfully
    assert (
        "Alarm sound played successfully." in log_contents
    ), "Expected log message not found in log file."

    # Check if the sound file exists (as in your original implementation)
    sound_file = os.path.join("resources", "sounds", "alarm_sound.wav")
    assert os.path.exists(sound_file), "Alarm sound file does not exist."


@then("I should see an error message")
def step_impl_error_message(context):
    assert context.error
