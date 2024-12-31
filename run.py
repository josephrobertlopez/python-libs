import argparse

from src.utils.module.ModuleRunnerSingleton import ModuleRunnerSingleton

if __name__ == "__main__":
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

    app = ModuleRunnerSingleton()
    app.setup()  # Ensure the setup is called before running
    app.run(args.module, args.module_args)
