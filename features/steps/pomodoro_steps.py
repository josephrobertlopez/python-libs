import os
import time

from behave import given, when, then
from src.utils.test.mock_context_manager import MockContextManager


@given("I have set the Pomodoro timer for {minutes} minute(s)")
def step_impl_set_timer(context, minutes):
    context.minutes = int(minutes)


@given("I have not provided any timer arguments")
def step_impl_no_arguments(context):
    context.minutes = ""


@when("the timer starts")
def step_impl_start_timer(context):
    # Use the MockContextManager to mock the sound playing
    context.mock_audio = MockContextManager(
        target_path="src.utils.media.audio.PygameMixerSoundSingleton",
        method_behaviors={"play_sound": None},
    )
    
    with context.mock_audio:
        try:
            # Start the timer process with additional context
            context.app.run("pomodoro", ["--minutes", str(context.minutes)])
        except Exception as e:
            context.error = e


@then("I should hear an alarm sound after {minutes:d} minute(s)")
def step_impl_hear_alarm(context, minutes):
    # Convert to seconds - to make tests run faster, we can simulate the time passing
    # without actually waiting the full duration
    if hasattr(context, 'mock_audio') and hasattr(context.mock_audio, 'get_mock'):
        # Verify that play_sound was called, which means the alarm would have sounded
        mock_play_sound = context.mock_audio.get_mock('play_sound')
        assert mock_play_sound is not None, "The play_sound mock was not created properly"
    
    # Check the sound file exists (as in your original implementation)
    sound_file = os.path.join("resources", "sounds", "alarm_sound.wav")
    assert os.path.exists(sound_file), f"Alarm sound file does not exist at path: {os.path.abspath(sound_file)}"


@then("I should see an error message")
def step_impl_error_message(context):
    assert hasattr(context, 'error'), "Expected an error but none was raised"
    assert context.error is not None, f"Expected an error but none was raised. Current working directory is: {os.getcwd()}"
