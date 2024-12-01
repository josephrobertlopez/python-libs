import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest
from src.utils.logging.logging_setup import (
    create_log_directory,
    initialize_log_files,
    load_logging_config,
    setup_logging,
    log_uncaught_exceptions,
)
from src.utils.test.MockManager import MockManager


def test_create_log_directory(mock_os):
    """Test create_log_directory"""
    with mock_os:
        create_log_directory("valid/log/dir")

    with pytest.raises(RuntimeError, match="Failed to create log directory"):
        mock_os.update_patch("path.exists", False)
        create_log_directory("invalid/log/dir")


def test_initialize_log_files_creates_log_file(mock_os, mock_builtins):
    """Test that initialize_log_files creates a single log file."""
    log_dir = "resources/logs"
    log_file = "app.log"
    mock_open = mock_builtins.get_mock("open")

    with mock_os.update_patch("path.exists", False) as mock_exists:
        initialize_log_files(log_dir, [log_file])
        mock_exists.assert_called_once_with("resources/logs/app.log")
        mock_open.assert_called_once_with("resources/logs/app.log", "w")

    with mock_os, mock_builtins:
        initialize_log_files(log_dir,[log_file])
        mock_open.assert_not_called()

def test_load_logging_config_calls_file_config(mock_logging):
    """Test load_logging_config loads the logging configuration."""
    config_path = "resources/logging_config.ini"

    load_logging_config(config_path)

    mock_logging.get_mock("config.fileConfig").assert_called_once_with(config_path)

def test_setup_logging_creates_log_directory(mock_os, mock_logging):
    """Test setup_logging creates the log directory."""
    config_ini_file = "resources/logging_config.ini"

    setup_logging(config_ini_file)

    # Verify that the log directory was created
    mock_os.get_mock("makedirs").assert_called_once_with("resources/logs")

    # Verify that the logging configuration was loaded
    mock_logging.get_mock("config.fileConfig").assert_called_once_with(config_ini_file)