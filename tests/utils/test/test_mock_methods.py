"""
Mock Methods Tests - Unified Factory Approach

Essential mock method testing using config-driven factory patterns.
"""

import unittest
from unittest.mock import Mock

from src.utils.test import StandardTestCase


class TestMockMethods(StandardTestCase):
    """Essential mock method tests using unified factory approach."""
    
    def test_method_called_basic(self):
        """Test basic method call detection."""
        mock = Mock()
        mock.test_method("arg1", "arg2")
        
        # Modern mock testing pattern
        mock.test_method.assert_called_with("arg1", "arg2")
        self.assertTrue(mock.test_method.called)
    
    def test_method_not_called(self):
        """Test method not called detection."""
        mock = Mock()
        
        # Modern mock testing pattern
        mock.test_method.assert_not_called()
        self.assertFalse(mock.test_method.called)
    
    def test_method_called_with_kwargs(self):
        """Test method call with keyword arguments."""
        mock = Mock()
        mock.test_method(arg1="value1", arg2="value2")
        
        result = mock.test_method.assert_called_with(arg1="value1", arg2="value2")
        self.assertTrue(mock.test_method.called)
    
    def test_method_called_with_different_args(self):
        """Test method call detection with different arguments."""
        mock = Mock()
        mock.test_method("wrong_arg")
        
        with self.assertRaises(AssertionError):
            mock.test_method.assert_called_with("correct_arg")


if __name__ == "__main__":
    unittest.main()
