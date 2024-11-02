import os
import subprocess
import time

from behave import given, when, then


@given("I have set the Pomodoro timer for {minutes:d} minute(s)")
def step_impl_set_timer(context, minutes):
    context.minutes = minutes
    context.timer_command = f"python3  run.py pomodoro --minutes {context.minutes}"
    context.process = subprocess.Popen(
        context.timer_command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


@given('I have set the Pomodoro timer for "{invalid_input}"')
def step_impl_set_invalid_timer(context, invalid_input):
    context.minutes = invalid_input
    context.timer_command = f"python3  run.py pomodoro --minutes {context.minutes}"
    context.process = subprocess.Popen(
        context.timer_command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


@given("I have not provided any timer arguments")
def step_impl_no_arguments(context):
    context.timer_command = f"python3  run.py pomodoro --minutes {context.minutes}"
    context.process = subprocess.Popen(
        context.timer_command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


@when("the timer starts")
def step_impl_start_timer(context):
    context.process.wait()  # Wait for the timer process to complete


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
    stdout, stderr = context.process.communicate()
    assert (
        context.process.returncode != 0
    ), "Process should not have completed successfully."
    assert (
        "error" in stderr.decode().lower()
    ), "Expected an error message, but did not find one."
