import subprocess
import sys
from behave import given, when, then
import pytest

@given('I have set the Pomodoro timer for {minutes}')
def step_set_timer(context, minutes):
    context.minutes = minutes

@when('the timer starts')
def step_start_timer(context):
    # Prepare command line arguments
    if context.minutes.isdigit():
        args = ["pomodoro.py", "-m", context.minutes]
        sys.argv = args
        context.result = subprocess.run(
            [sys.executable, "-m", "src.pomodoro.pomodoro"],
            capture_output=True,
            text=True
        )
    else:
        context.result = subprocess.run(
            [sys.executable, "-m", "src.pomodoro.pomodoro"],
            input=context.minutes,
            capture_output=True,
            text=True
        )

@then('I should hear an alarm sound after {minutes} minute')
def step_hear_alarm(context, minutes):
    assert context.result.returncode == 0
    assert "Pomodoro timer set for" in context.result.stdout
    # You may need to check for the specific sound file being played if desired

@then('I should see an error message')
def step_error_message(context):
    assert context.result.returncode != 0
    assert "Error" in context.result.stderr  # Adjust based on actual error message output
