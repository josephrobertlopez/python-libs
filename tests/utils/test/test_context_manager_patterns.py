"""
Context Manager Patterns - Unified Factory Approach

Demonstrates config-driven context patterns using the unified mock framework.
"""

import unittest
import sys
import os
from unittest.mock import Mock
from io import StringIO

from src.utils.test import StandardTestCase, runtime_mock, runtime_context


class TestContextManagerPatterns(StandardTestCase):
    """Test context manager patterns using unified factory approach."""

    def test_basic_context_with_factory_config(self):
        """Test basic context using factory config."""
        config = {"sys": {"argv": ["test_app"], "executable": "/usr/bin/python3"}}

        with runtime_context(config) as ctx:
            self.assertEqual(sys.argv, ["test_app"])

    def test_nested_context_composition(self):
        """Test composing nested contexts with factory configs."""
        with runtime_context({"sys": {"argv": ["composed_test"]}}):
            with runtime_context({"sys": {"executable": "/usr/bin/python3"}}):
                self.assertEqual(sys.argv, ["composed_test"])
                self.assertEqual(sys.executable, "/usr/bin/python3")

    @runtime_mock({"os": {"path": {"exists": lambda path: path == "/data/input.txt"}}})
    def test_file_system_pattern(self):
        """File system mocking using factory annotation."""
        self.assertTrue(os.path.exists("/data/input.txt"))
        self.assertFalse(os.path.exists("/data/output.txt"))

    def test_dynamic_context_updates(self):
        """Test dynamic context using factory approach."""
        with runtime_context({"sys": {"argv": ["initial"]}}) as ctx:
            self.assertEqual(sys.argv, ["initial"])

            # Test that the context object exists and has config
            self.assertIsInstance(ctx.config, dict)
            self.assertIn("sys", ctx.config)


if __name__ == "__main__":
    unittest.main()
