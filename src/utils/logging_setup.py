# src/utils/logging_setup.py

import os
import logging
import logging.config
import sys
from src.utils.get_resource_path import get_resource_path

def setup_logging():
    if getattr(sys, 'frozen', False):  # Running as a PyInstaller executable
        logging.disable(logging.CRITICAL)  # Disable all logging
        return

    # Ensure the log directory exists
    log_dir = 'resources/logs'
    os.makedirs(log_dir, exist_ok=True)

    # Create the log files if they don't exist
    for log_file in ['app.log', 'error.log']:
        log_file_path = os.path.join(log_dir, log_file)
        if not os.path.exists(log_file_path):
            open(log_file_path, 'w').close()  # Create an empty log file

    # Load logging configuration from the .ini file
    logging.config.fileConfig(get_resource_path('resources/logging_config.ini'))
