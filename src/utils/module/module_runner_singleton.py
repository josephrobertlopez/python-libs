import os
import sys
import importlib
from src.utils.abstract.abstract_runner import AbstractRunner
from src.utils.env_checks.env_checks import load_environment_variables, get_env_var
from src.utils.logging.logging_config_singleton import LoggingConfigSingleton
from src.utils.abstract.abstract_singleton import AbstractSingleton


class ModuleRunnerSingleton(AbstractSingleton):
    def __init__(self):
        pass

    def _setup(self):
        """Initialize environment variables and logging."""
        if getattr(sys, "frozen", False):
            # If the script is frozen (e.g., PyInstaller executable)
            env_file_path = os.path.join(sys._MEIPASS, ".env")
            load_environment_variables(env_file_path)
            get_env_var("LOG_CONFIG_FILE")
            return

        load_environment_variables(".env")
        # Set up logging
        logger_setup = LoggingConfigSingleton(
            config_path=get_env_var("LOG_CONFIG_FILE"), 
            log_dir=os.path.join("resources", "logs")
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
            module = importlib.import_module(f"src.runners.{module_name}")

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
