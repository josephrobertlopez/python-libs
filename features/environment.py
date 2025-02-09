import shutil
import os

from src.utils.module.module_runner_singleton import ModuleRunnerSingleton


def before_all(context):
    context.app = ModuleRunnerSingleton()
    context.app.setup()


def after_all(context):
    del context.app
    if os.path.exists("resources/logs"):
        shutil.rmtree("resources/logs")
