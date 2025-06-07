import unittest
from unittest.mock import Mock, patch

import sys
import os
import json

from src.utils.test.smart_mock import smart_mock, patch_object, create_mock_class


# Sample class for testing, not a test class
class TestClass:
    def method_to_test(self):
        return "original"

    def another_method(self, value):
        return value * 2


class TestObject:
    attribute = "original"

    def method(self, value):
        return value * 3


def test_smart_mock_context_manager():
    """Test smart_mock context manager with different types of mocks."""
    # Save original dumps function to avoid affecting other tests
    original_dumps = json.dumps

    with smart_mock(
        "json",  # Use json module which definitely exists
        dumps=lambda obj, **kwargs: f"MOCKED: {obj}",  # Accept **kwargs to handle any parameters
        loads=lambda s, **kwargs: {
            "mocked": True
        },  # Accept **kwargs to handle any parameters
        JSONDecodeError="MOCKED_ERROR",  # Use a real attribute from json module
        decoder={"key": "value"},
        encoder=[1, 2, 3],
    ) as mock_ctx:
        # Test function mocks
        assert json.dumps({"test": 123}) == "MOCKED: {'test': 123}"
        assert json.loads("whatever") == {"mocked": True}

        # Test attribute mock
        assert json.JSONDecodeError == "MOCKED_ERROR"

        # Test dict mock
        assert json.decoder["key"] == "value"

        # Test list mock
        assert json.encoder[0] == 1

        # Test adding a mock during runtime
        mock_ctx.add_mock("new_function", lambda: "dynamic")
        assert json.new_function() == "dynamic"


def test_patch_object():
    """Test patch_object function for patching attributes on objects."""
    test_obj = TestObject()

    # Original behavior
    assert test_obj.attribute == "original"
    assert test_obj.method(3) == 9

    # Patch attribute
    with patch_object(test_obj, "attribute", "mocked"):
        assert test_obj.attribute == "mocked"

    # Original value restored
    assert test_obj.attribute == "original"

    # Patch method
    with patch_object(test_obj, "method", lambda x: x * 10):
        assert test_obj.method(3) == 30

    # Original method restored
    assert test_obj.method(3) == 9


def test_create_mock_class():
    """Test create_mock_class for creating mock classes."""
    # Create a mock class with methods and attributes
    MockClass = create_mock_class(
        class_methods={
            "test_method": lambda self: "mocked method",  # Add self parameter
            "param_method": lambda self, x: x * 5,  # Add self parameter
            "return_value_method": "static result",  # Test non-callable return value
        },
        class_attributes={
            "CONSTANT": 42,
            "name": "test_name",
        },
    )

    # Create an instance
    mock_instance = MockClass()

    # Test methods
    assert mock_instance.test_method() == "mocked method"
    assert mock_instance.param_method(4) == 20
    assert (
        mock_instance.return_value_method() == "static result"
    )  # Test method with static return

    # Test attributes
    assert mock_instance.CONSTANT == 42
    assert mock_instance.name == "test_name"
