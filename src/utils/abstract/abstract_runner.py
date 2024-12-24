import argparse
from abc import ABC, abstractmethod


class AbstractRunner(ABC):
    """Abstract runner class to handle argument parsing and define the main method."""

    def __init__(self):
        """Initialize the runner."""
        pass

    def parse_arguments(self, *args, **kwargs):
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
