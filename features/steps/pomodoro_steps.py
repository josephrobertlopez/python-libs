import os
import time

from behave import given, when, then
from src.utils.test.smart_mock import smart_mock, create_mock_class
from unittest.mock import MagicMock


@given("I have set the Pomodoro timer for {minutes} minute(s)")
def step_impl_set_timer(context, minutes):
    context.minutes = int(minutes)


@given("I have not provided any timer arguments")
def step_impl_no_arguments(context):
    context.minutes = ""


@when("the timer starts")
def step_impl_start_timer(context):
    # Create a mock for the PygameMixerSoundSingleton class
    mock_play_sound = MagicMock()
    
    # Create a mock class with the required methods
    MockAudioClass = create_mock_class(
        class_methods={
            "load_sound": lambda self, file_path: None,
            "play_sound": lambda self, *args, **kwargs: mock_play_sound(*args, **kwargs),
            "is_sound_playing": lambda self: True
        }
    )
    
    # Use the smart_mock context manager to mock the class
    with smart_mock(
        "src.utils.media.audio",
        PygameMixerSoundSingleton=MockAudioClass
    ) as mock_ctx:
        # Store both the context and the specific mock function for later verification
        context.mock_audio = mock_ctx
        context.mock_play_sound = mock_play_sound
        
        try:
            # Start the timer process with additional context
            context.app.run("pomodoro", ["--minutes", str(context.minutes)])
        except Exception as e:
            context.error = e


@then("I should hear an alarm sound after {minutes:d} minute(s)")
def step_impl_hear_alarm(context, minutes):
    # Verify that play_sound was called, which means the alarm would have sounded
    assert hasattr(context, 'mock_play_sound'), "The play_sound mock was not created properly"
    assert context.mock_play_sound.called, "The play_sound method was not called"
    
    # Check the sound file exists
    sound_file = os.path.join("resources", "sounds", "alarm_sound.wav")
    assert os.path.exists(sound_file), f"Alarm sound file does not exist at path: {os.path.abspath(sound_file)}"


@then("I should see an error message")
def step_impl_error_message(context):
    assert hasattr(context, 'error'), "Expected an error but none was raised"
    assert context.error is not None, f"Expected an error but none was raised. Current working directory is: {os.getcwd()}"
