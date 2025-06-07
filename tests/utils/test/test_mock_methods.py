import unittest
from unittest.mock import MagicMock
import io
from contextlib import redirect_stdout

from src.utils.test.mock_methods import method_called_in_mock


class TestMockMethods(unittest.TestCase):

    def test_method_called_with_matching_args(self):
        # Create a mock with a method call
        mock = MagicMock()
        mock.some_method(1, 2, 3)

        # Test with matching args
        f = io.StringIO()
        with redirect_stdout(f):
            result = method_called_in_mock(mock, "some_method", 1, 2, 3)

        self.assertTrue(result)
        self.assertIn("method some_method called with args", f.getvalue())

    def test_method_called_with_different_args(self):
        # Create a mock with a method call
        mock = MagicMock()
        mock.some_method(1, 2, 3)

        # Test with different args
        f = io.StringIO()
        with redirect_stdout(f):
            result = method_called_in_mock(mock, "some_method", 4, 5, 6)

        self.assertFalse(result)
        self.assertIn("method some_method not called with args", f.getvalue())

    def test_method_not_called(self):
        # Create a mock with no method calls
        mock = MagicMock()

        # Test for a method that was never called
        f = io.StringIO()
        with redirect_stdout(f):
            result = method_called_in_mock(mock, "some_method", 1, 2, 3)

        self.assertFalse(result)
        self.assertIn("method call of some_method not found on mock", f.getvalue())
