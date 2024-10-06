from behave import given, when, then
import subprocess
import time
import os

@given('I have set the Pomodoro timer for {minutes:d} minute(s)')
def step_impl_set_timer(context, minutes):
    context.minutes = minutes
    context.timer_command = f'python3 -m src.pomodoro.pomodoro -m {context.minutes}'
    context.process = subprocess.Popen(context.timer_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

@given('I have set the Pomodoro timer for "{invalid_input}"')
def step_impl_set_invalid_timer(context, invalid_input):
    context.minutes = invalid_input
    context.timer_command = f'python3 -m src.pomodoro.pomodoro -m {context.minutes}'
    context.process = subprocess.Popen(context.timer_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

@given('I have not provided any timer arguments')
def step_impl_no_arguments(context):
    context.timer_command = 'python3 -m src.pomodoro.pomodoro'  # No arguments provided
    context.process = subprocess.Popen(context.timer_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

@when('the timer starts')
def step_impl_start_timer(context):
    context.process.wait()  # Wait for the timer process to complete

@then('I should hear an alarm sound after {minutes:d} minute(s)')
def step_impl_hear_alarm(context, minutes):
    # Wait for the specified minutes (use `time.sleep` to simulate the waiting period)
    time.sleep(minutes * 60)  # Adjust to full minutes instead of 59 seconds
    
    # Capture the output and error logs from the process
    stdout, stderr = context.process.communicate()

    # Check if the alarm sound played successfully
    output = stdout.decode() + stderr.decode()  # Combine standard output and error
    assert "Alarm sound played successfully." in output, "Expected log message not found in output."

    # Check if the sound file exists (as in your original implementation)
    sound_file = os.path.join("resources", "sounds", "alarm_sound.wav")
    assert os.path.exists(sound_file), "Alarm sound file does not exist."

@then('I should see an error message')
def step_impl_error_message(context):

    stdout, stderr = context.process.communicate()
    assert context.process.returncode != 0, "Process should not have completed successfully."
    assert "error" in stderr.decode().lower(), "Expected an error message, but did not find one."
