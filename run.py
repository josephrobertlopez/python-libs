import argparse
import importlib
from src.utils.env.env_checks import load_environment_variables, get_env_var
from src.utils.logging.logging_setup import setup_logging


def main(module_name: str, module_args: list) -> None:
    """
    Dynamically import and run the specified module.

    :param module_name: Name of the module to run (e.g., 'pomodoro').
    :param module_args: Arguments to pass to the module's main function.
    """
    module = importlib.import_module(f"src.{module_name}.{module_name}")
    # Pass all arguments to the module's main function
    module.main(*module_args)


if __name__ == "__main__":
    load_environment_variables(".env")

    LOG_CONFIG_FILE = get_env_var("LOG_CONFIG_FILE")
    setup_logging(LOG_CONFIG_FILE)

    parser = argparse.ArgumentParser(description="Run the specified module.")
    parser.add_argument(
        "module",
        type=str,
        help="The name of the module to run (e.g., 'pomodoro'.")

    # Capture any additional arguments
    parser.add_argument(
        "module_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments for the module.",
    )

    args = parser.parse_args()

    # Pass the captured module arguments to main
    main(args.module, args.module_args)
