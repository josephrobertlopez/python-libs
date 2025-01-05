from unittest.mock import patch, MagicMock

import pytest
from src.utils.module.ModuleRunnerSingleton import (
    ModuleRunnerSingleton,
)  # Correct class import


def test_create_runner_fail_class_not_inheriting_AbstractRunner():
    # Test that create_runner raises an error if the class doesn't inherit AbstractRunner
    mock_module = MagicMock()

    # Create a mock class that does not inherit from AbstractRunner
    mock_runner_class = MagicMock()

    # Mock that the class does not inherit from AbstractRunner
    mock_runner_class.__class__ = (
        object  # Ensure it's just a plain class, not inheriting from AbstractRunner
    )
    mock_module.PomodoroRunner = mock_runner_class

    # Instantiate ModuleRunnerSingleton and try to create the runner
    module_runner = ModuleRunnerSingleton()
    module_runner._setup()
    module_runner.create_runner("pomodoro")

    with patch("importlib.import_module", return_value=False):
        with pytest.raises(ValueError, match="No runner class found"):
            module_runner.create_runner("pomodoro")


def test_run():
    # Test that the run method works as expected
    module_runner = ModuleRunnerSingleton()
    with patch.object(
        module_runner, "create_runner", return_value=MagicMock()
    ) as mock_create_runner:
        module_runner.run("pomodoro", ["-m", "0"])
        mock_create_runner.assert_called_once()
