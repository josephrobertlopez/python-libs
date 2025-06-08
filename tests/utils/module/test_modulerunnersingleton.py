import pytest
from unittest.mock import MagicMock
from src.utils.module.module_runner_singleton import (
    ModuleRunnerSingleton,
)  # Correct class import
from src.utils.test import smart_mock, patch_object


def test_create_runner_fail_class_not_inheriting_AbstractRunner():
    """Test that create_runner raises an error if the class does not inherit from AbstractRunner."""
    mock_module = MagicMock()

    # Create a mock class that does NOT inherit from AbstractRunner
    class MockRunner:
        pass  # This class does not extend AbstractRunner

    mock_module.PomodoroRunner = MockRunner  # Assign mock class to the module

    with smart_mock("importlib", import_module=lambda module_name: mock_module):
        module_runner = ModuleRunnerSingleton()

        # Expecting ValueError since the class doesn't inherit from AbstractRunner
        with pytest.raises(
            ValueError, match="No runner class found or class does not inherit"
        ):
            module_runner.create_runner("pomodoro")


def test_run():
    """Test that the run method works as expected using smart_mock utilities."""
    module_runner = ModuleRunnerSingleton()
    mock_runner = MagicMock()
    
    with patch_object(module_runner, "create_runner", mock_runner):
        module_runner.run("pomodoro", ["-m", "0"])
        mock_runner.assert_called_once()
