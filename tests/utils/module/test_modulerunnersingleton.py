from unittest.mock import patch, MagicMock

import pytest
from src.utils.module.ModuleRunnerSingleton import (
    ModuleRunnerSingleton,
)  # Correct class import


def test_create_runner_fail_class_not_inheriting_AbstractRunner():
    """Test that create_runner raises an error if the class does not inherit from AbstractRunner."""
    mock_module = MagicMock()

    # Create a mock class that does NOT inherit from AbstractRunner
    class MockRunner:
        pass  # This class does not extend AbstractRunner

    mock_module.PomodoroRunner = MockRunner  # Assign mock class to the module

    with patch("importlib.import_module", return_value=mock_module):
        module_runner = ModuleRunnerSingleton()

        # Expecting ValueError since the class doesn't inherit from AbstractRunner
        with pytest.raises(
            ValueError, match="No runner class found or class does not inherit"
        ):
            module_runner.create_runner("pomodoro")


def test_run():
    # Test that the run method works as expected
    module_runner = ModuleRunnerSingleton()
    with patch.object(
        module_runner, "create_runner", return_value=MagicMock()
    ) as mock_create_runner:
        module_runner.run("pomodoro", ["-m", "0"])
        mock_create_runner.assert_called_once()
