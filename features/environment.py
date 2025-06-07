import shutil
import os

from src.utils.module.module_runner_singleton import ModuleRunnerSingleton


def before_all(context):
    context.app = ModuleRunnerSingleton()
    context.app.setup()


def after_all(context):
    del context.app
    log_dir = os.path.join("resources", "logs")
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
