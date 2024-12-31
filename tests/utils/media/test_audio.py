def test_load_sound(mock_singleton_setup, mixer, pygame_mixer_audio):
    with pygame_mixer_audio:
        mixer.load_sound("Fake_sound.wav")
        pygame_mixer_audio.get_mock("Sound").assert_called_once()
    with pygame_mixer_audio.remove_patch("Sound") as m:
        del m
        mixer.load_sound("Fake_sound.wav")


def test_play_sound(mock_singleton_setup, mixer, pygame_mixer_audio):
    # Mocking the pygame.mixer.Sound class to simulate successful sound playback
    with pygame_mixer_audio:
        # Run the play_alarm_sound method
        # Assert that the play method was called once
        mixer.load_sound("Fake_sound.wav")
        mixer.play_sound(until_time=0)
        pygame_mixer_audio.get_mock("Sound")().play.assert_called_once()


def test_is_sound_playing(mock_singleton_setup, mixer, pygame_mixer_audio):
    """Test that is_sound_playing returns True when sound is playing."""
    with pygame_mixer_audio:
        assert not mixer.is_sound_playing()
        mixer.load_sound("Fake_sound.wav")
        assert mixer.is_sound_playing()
