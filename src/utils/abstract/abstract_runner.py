import argparse
from abc import ABC, abstractmethod


class AbstractRunner(ABC):
    """Abstract runner class to handle argument parsing and define the main method."""

    def __init__(self, *args):
        """Initialize the runner."""
        self.parsed_args = None
        self._arguments_initialized = False

    @staticmethod
    def parse_arguments(*args, **kwargs):
        """Parse command-line arguments dynamically based on kwargs.

        Args:
            *args: The arguments to parse (typically passed from the command line).
            **kwargs: A dictionary where keys are argument names and values are argument configurations.

        Returns:
            Namespace: Parsed arguments as a namespace object.
        """
        parser = argparse.ArgumentParser()

        # Dynamically add arguments from kwargs
        for arg_name, arg_config in kwargs.items():
            parser.add_argument(arg_name, **arg_config)

        parsed_args = parser.parse_args(args)
        return parsed_args

    @property
    @abstractmethod
    def argument_definitions(self):
        """Defines the arguments for the command-line parser.

        Returns:
            dict: A dictionary of argument names and their configurations.
        """
        pass

    def initialized_arguments(self, *args):
        if not self.argument_definitions:
            raise NotImplementedError(
                "Subclasses must define 'argument_definitions' to use initialize_argumsnts()"
            )
        self.parsed_args = self.parse_arguments(*args, **self.argument_definitions)
        self._arguments_initialized = True

    def run(self, *args):
        self.main(*args)
        if not self._arguments_initialized:
            raise RuntimeError(
                "The 'initialize_arguments' method must be called in the 'main' method of subclasses."
            )

    @abstractmethod
    def main(self) -> None:
        """Main method to execute the application logic."""
        pass


class SampleConcreteRunner(AbstractRunner):
    """Concrete implementation of AbstractRunner."""

    @property
    def argument_definitions(self):
        return {
            "--name": {"help": "Your name", "required": True},
            "--age": {
                "help": "Your age",
                "type": int,
                "required": False,
                "default": 30,
                "dest": "age",
            },
            "-a": {"help": "Your age", "dest": "age"},
        }

    def main(self, *args):
        # Parse *args with parse_arguments method
        self.initialized_arguments(*args)
        print(
            f"Hello {self.parsed_args.name}, I see you are {self.parsed_args.age} years old."
        )
