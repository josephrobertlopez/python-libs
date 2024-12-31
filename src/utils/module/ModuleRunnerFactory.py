import importlib
from src.utils.abstract.abstract_runner import AbstractRunner


class ModuleRunnerFactory:
    def __init__(self, module_name: str, module_args: list) -> None:
        """
        Initializes the factory with the module name and arguments to run.
        :param module_name: Name of the module to run (e.g., 'pomodoro').
        :param module_args: Arguments to pass to the module's main function.
        """
        self.module_name = module_name
        self.module_args = module_args

    def create_runner(self):
        """
        Dynamically imports and instantiates a runner class that inherits from AbstractRunner.
        :return: An instance of the runner class.
        """
        try:
            # Dynamically import the runner module (e.g., src.pomodoro.pomodoro)
            module = importlib.import_module(
                f"src.{self.module_name}.{self.module_name}"
            )

            # Check if the module has a class that inherits from AbstractRunner
            runner_class = getattr(
                module, self.module_name.capitalize() + "Runner", None
            )

            if runner_class and issubclass(runner_class, AbstractRunner):
                return runner_class()
            else:
                raise ValueError(
                    f"No runner class found or class does not inherit from AbstractRunner in {self.module_name}."
                )
        except ImportError:
            raise ValueError(
                f"Module '{self.module_name}' not found. Please check the module name."
            )
