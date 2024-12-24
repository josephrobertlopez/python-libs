import argparse
import importlib
from src.utils.env_checks.env_checks import load_environment_variables, get_env_var
from src.utils.logging.LoggingConfigSingleton import LoggingConfigSingleton
from src.utils.abstract.abstract_runner import AbstractRunner  # Import AbstractRunner


def main(module_name: str, module_args: list) -> None:
    """
    Dynamically import and run the specified module, delegating to the runner class.

    :param module_name: Name of the module to run (e.g., 'pomodoro').
    :param module_args: Arguments to pass to the module's main function.
    """
    # Try to dynamically import and instantiate a runner class that inherits from AbstractRunner
    try:
        # Dynamically import the runner module (e.g., src.pomodoro.pomodoro)
        module = importlib.import_module(f"src.{module_name}.{module_name}")

        # Check if the module has a class that inherits from AbstractRunner
        runner_class = getattr(module, module_name.capitalize() + "Runner", None)

        if runner_class and issubclass(runner_class, AbstractRunner):
            runner = runner_class()
            runner.main(*module_args)  # Run the main method of the runner
        else:
            print(
                f"No runner class found or class does not inherit from AbstractRunner in {module_name}."
            )

    except ImportError:
        print(f"Module '{module_name}' not found. Please check the module name.")


if __name__ == "__main__":
    load_environment_variables(".env")

    LOG_CONFIG_FILE = get_env_var("LOG_CONFIG_FILE")
    logger_setup = LoggingConfigSingleton(LOG_CONFIG_FILE)
    logger_setup.setup()

    parser = argparse.ArgumentParser(description="Run the specified module.")
    parser.add_argument(
        "module", type=str, help="The name of the module to run (e.g., 'pomodoro')."
    )

    # Capture any additional arguments
    parser.add_argument(
        "module_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments for the module.",
    )

    args = parser.parse_args()

    # Pass the captured module arguments to the main function
    main(args.module, args.module_args)
