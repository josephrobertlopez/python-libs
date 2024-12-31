import argparse
from abc import ABC, abstractmethod


class AbstractRunner(ABC):
    """Abstract runner class to handle argument parsing and define the main method."""

    def __init__(self):
        """Initialize the runner."""
        pass

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

    @abstractmethod
    def main(self, *args) -> None:
        """Main method to execute the application logic."""
        pass


class SampleConcreteRunner(AbstractRunner):
    """Concrete implementation of AbstractRunner."""

    def main(self, *args):
        # Parse *args with parse_arguments method
        parsed_args = self.parse_arguments(
            **{
                "--name": {"help": "Your name", "required": True},
                "--age": {
                    "help": "Your age",
                    "type": int,
                    "required": False,
                    "default": 30,
                },
            }
        )
        print(f"Hello {parsed_args.name}, I see you are {parsed_args.age} years old.")
