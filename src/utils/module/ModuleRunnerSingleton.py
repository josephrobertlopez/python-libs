from src.utils.env_checks.env_checks import load_environment_variables, get_env_var
from src.utils.logging.LoggingConfigSingleton import LoggingConfigSingleton
from src.utils.abstract.abstract_singleton import AbstractSingleton
from src.utils.module.ModuleRunnerFactory import ModuleRunnerFactory


class ModuleRunnerSingleton(AbstractSingleton):
    def __init__(self):
        self.module_name = None
        self.module_args = None

    def _setup(self):
        """Initialize environment variables and logging."""
        self.load_environment_variables()
        self.setup_logging()

    def load_environment_variables(self):
        """Loads environment variables."""
        load_environment_variables(".env")

    def setup_logging(self):
        """Sets up the logging configuration."""
        LOG_CONFIG_FILE = get_env_var("LOG_CONFIG_FILE")
        logger_setup = LoggingConfigSingleton(LOG_CONFIG_FILE)
        logger_setup.setup()

    def run(self, module_name: str, module_args: list):
        """Main function to dynamically load and execute the runner for a module."""
        self.module_name = module_name
        self.module_args = module_args
        factory = ModuleRunnerFactory(module_name, module_args)
        runner = factory.create_runner()
        runner.run(*module_args)
