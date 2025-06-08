import pytest
from unittest.mock import MagicMock, patch
from src.runners.pomodoro import PomodoroRunner
from tests.shared_annotations import StandardTestCase, mock_test_os, audio_test


class TestPomodoroRunner(StandardTestCase):
    """Test class for PomodoroRunner using smart annotations."""

    @mock_test_os(environ={"SOUND_FILE": "test_sound_file.wav"})
    @audio_test()
    def test_pomodoro_runner(self, **kwargs):
        """Test PomodoroRunner behavior with 1-minute session."""
        # Mock time.sleep properly within the test
        with patch("time.sleep") as mock_sleep:
            # Initialize PomodoroRunner
            runner = PomodoroRunner()

            # Simulate passing arguments for minutes
            args = ["-m", "1"]  # 1-minute Pomodoro session

            # Run the main method
            runner.main(*args)

            # Verify time.sleep was called with 60 seconds
            mock_sleep.assert_called_once_with(60)
