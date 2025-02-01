import os
import sys
import importlib
from src.utils.abstract.abstract_runner import AbstractRunner
from src.utils.env_checks.env_checks import load_environment_variables, get_env_var
from src.utils.logging.LoggingConfigSingleton import LoggingConfigSingleton
from src.utils.abstract.abstract_singleton import AbstractSingleton


class ModuleRunnerSingleton(AbstractSingleton):
    def __init__(self):
        pass

    def _setup(self):
        """Initialize environment variables and logging."""
        # Determine the base directory
        frozen_path = ""
        if getattr(sys, "frozen", False):
            # If the script is frozen (e.g., PyInstaller executable)
            frozen_path = sys._MEIPASS
        env_file_path = os.path.join(frozen_path, ".env")
        log_dir = os.path.join(frozen_path, "resources/logs")

        # Load env var
        load_environment_variables(env_file_path)
        log_config_file = get_env_var("LOG_CONFIG_FILE")

        log_config_file_path = os.path.join(frozen_path, log_config_file)
        # Load the environment variables

        # Set up logging
        logger_setup = LoggingConfigSingleton(
            config_path=log_config_file_path, log_dir=log_dir
        )
        logger_setup.setup()

    @staticmethod
    def create_runner(module_name):
        """
        Dynamically imports and instantiates a runner class that inherits from AbstractRunner.
        :return: An instance of the runner class.
        """
        try:
            # Dynamically import the runner module (e.g., src.pomodoro.pomodoro)
            module = importlib.import_module(f"src.{module_name}.{module_name}")

            # Check if the module has a class that inherits from AbstractRunner
            runner_class = getattr(module, module_name.capitalize() + "Runner", None)

            if runner_class and issubclass(runner_class, AbstractRunner):
                return runner_class()
            else:
                raise ValueError(
                    f"No runner class found or class does not inherit from AbstractRunner in {module_name}."
                )
        except ImportError:
            raise ValueError(
                f"Module '{module_name}' not found. Please check the module name."
            )

    def run(self, module_name: str, module_args: list):
        """Main function to dynamically load and execute the runner for a module."""
        runner = self.create_runner(module_name)
        runner.run(*module_args)
