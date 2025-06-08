import unittest
from unittest.mock import Mock, patch
import pytest

from tests.shared_annotations import (
    StandardTestCase,
    mock_test_module,
    mock_logging_context,
)
from src.utils.logging.logging_config_singleton import LoggingConfigSingleton


def create_mock_logger():
    """Create a mock logger for testing."""
    logger = Mock()
    logger.info = Mock()
    logger.debug = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    logger.setLevel = Mock()
    logger.addHandler = Mock()
    return logger


class TestLoggingSetup(StandardTestCase):

    def setUp(self):
        """Set up test instance."""
        super().setUp()
        # Mock the cross-platform config generator to avoid real temp file creation
        with patch(
            "src.utils.logging.logging_config_singleton.generate_cross_platform_logging_config",
            return_value="/fake/path/logging_config.ini",
        ):
            self.logging_setup = LoggingConfigSingleton(
                config_path="path/to/config.ini", log_files=["app.log"]
            )
        # Reset setup state for testing
        self.logging_setup._setup_called = False

    @mock_test_module(
        "logging.config",
        fileConfig=Mock(side_effect=FileNotFoundError("Config file doesn't exist")),
    )
    def test_logging_setup_logging_file_dne(self):
        """Test logging setup when log file doesn't exist."""
        # The setup should raise RuntimeError wrapping FileNotFoundError
        with pytest.raises(
            RuntimeError,
            match="Failed to load logging configuration.*Config file doesn't exist",
        ):
            self.logging_setup.setup()

    @mock_test_module("logging.config", fileConfig=Mock())
    def test_logging_setup(self):
        """Test normal logging setup."""
        with mock_logging_context():
            self.logging_setup.setup()

    @mock_test_module(
        "logging.config",
        fileConfig=Mock(side_effect=Exception("Failed to load config")),
    )
    def test_logging_failed_config_load(self):
        """Test logging setup with failed config load."""
        # The setup should raise RuntimeError wrapping the original exception
        with pytest.raises(
            RuntimeError,
            match="Failed to load logging configuration.*Failed to load config",
        ):
            self.logging_setup.setup()
