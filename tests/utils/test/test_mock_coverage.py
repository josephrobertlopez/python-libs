"""
Mock Coverage Tests - Unified Factory Approach

Essential coverage tests using config-driven factory patterns.
"""

import unittest
import sys
import os
from unittest.mock import Mock
from io import StringIO

from src.utils.test import StandardTestCase, smart_mock


class TestMockCoverage(StandardTestCase):
    """Essential mock coverage tests using unified factory approach."""
    
    def test_basic_mock_coverage(self):
        """Test basic mock functionality with factory config."""
        config = {"sys": {"argv": ["test_app"], "executable": "test_executable"}}
        
        with smart_mock("sys", **config["sys"]):
            self.assertEqual(sys.argv, ["test_app"])
            self.assertEqual(sys.executable, "test_executable")
    
    def test_context_manager_coverage(self):
        """Test context manager functionality."""
        with smart_mock("sys", argv=["coverage_test"]) as ctx:
            self.assertEqual(sys.argv, ["coverage_test"])
            
            # Test context manager utilities
            self.assertTrue(hasattr(ctx, 'get_mock'))
            self.assertTrue(hasattr(ctx, 'update_mock'))
    
    def test_multiple_module_coverage(self):
        """Test mocking multiple modules."""
        sys_config = {"argv": ["multi_test"]}
        os_config = {"getcwd": lambda: "/test/coverage"}
        
        with smart_mock("sys", **sys_config):
            with smart_mock("os", **os_config):
                self.assertEqual(sys.argv, ["multi_test"])
                self.assertEqual(os.getcwd(), "/test/coverage")
    
    def test_mock_validation_coverage(self):
        """Test mock validation and error handling."""
        with smart_mock("sys", argv=["validation"]):
            # Verify mock is applied
            self.assertEqual(sys.argv, ["validation"])
        
        # Verify cleanup after context
        self.assertNotEqual(sys.argv, ["validation"])


if __name__ == "__main__":
    unittest.main()
