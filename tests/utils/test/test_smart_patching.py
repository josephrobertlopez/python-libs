import unittest
from unittest.mock import Mock, patch

import sys
import os
from collections.abc import Mapping

from src.utils.test.mock_patching_strategies import SmartPatcherStrategy
from src.utils.test.mock_context_manager import MockContextManager


class SampleClass:
    def method(self):
        return "original"


def test_smart_patcher_with_callable():
    """Test SmartPatcherStrategy with a callable function."""
    strategy = SmartPatcherStrategy()
    # Use sys module which is guaranteed to exist
    patcher = strategy.execute("sys", "test_function", lambda x: x * 2)
    mock_obj = patcher.start()

    try:
        assert sys.test_function(5) == 10
    finally:
        patcher.stop()


def test_smart_patcher_with_dict():
    """Test SmartPatcherStrategy with a dictionary."""
    strategy = SmartPatcherStrategy()
    # Use os module which is guaranteed to exist
    patcher = strategy.execute("os", "test_dict", {"a": 1, "b": 2})
    mock_obj = patcher.start()

    try:
        assert os.test_dict["a"] == 1
        assert os.test_dict["b"] == 2
    finally:
        patcher.stop()


def test_smart_patcher_with_list():
    """Test SmartPatcherStrategy with a list."""
    strategy = SmartPatcherStrategy()
    # Use os module which is guaranteed to exist
    patcher = strategy.execute("os", "test_list", [1, 2, 3])
    mock_obj = patcher.start()

    try:
        assert os.test_list[0] == 1
        assert os.test_list[1] == 2
        assert os.test_list[2] == 3
    finally:
        patcher.stop()


def test_smart_patcher_with_class():
    """Test SmartPatcherStrategy with a class."""
    strategy = SmartPatcherStrategy()
    # Use sys module which is guaranteed to exist
    patcher = strategy.execute("sys", "TestClass", SampleClass)
    mock_obj = patcher.start()

    try:
        obj = sys.TestClass()
        assert obj.method() == "original"
    finally:
        patcher.stop()


def test_smart_patcher_with_none():
    """Test SmartPatcherStrategy with None."""
    strategy = SmartPatcherStrategy()
    # Use sys module which is guaranteed to exist
    patcher = strategy.execute("sys", "test_none", None)
    mock_obj = patcher.start()

    try:
        assert sys.test_none is None
    finally:
        patcher.stop()


def test_mock_context_manager_with_auto_mock():
    """Test MockContextManager with auto mock detection."""
    # Use sys module which is guaranteed to exist
    mock_ctx = MockContextManager(
        target_path="sys",
        auto_mock={
            "function": lambda x: x * 3,
            "dict_value": {"a": 1, "b": 2},
            "list_value": [1, 2, 3],
            "simple_value": 42,
            "class_type": SampleClass,
        },
    )

    with mock_ctx:
        # Check function mock
        assert sys.function(5) == 15

        # Check dict mock
        assert sys.dict_value["a"] == 1
        assert sys.dict_value["b"] == 2

        # Check list mock
        assert sys.list_value[0] == 1
        assert len(sys.list_value) == 3

        # Check simple value mock
        assert sys.simple_value == 42

        # Check class mock
        obj = sys.class_type()
        assert obj.method() == "original"


def test_dynamic_mock_addition():
    """Test adding mocks dynamically during runtime."""
    # Use os module which is guaranteed to exist
    mock_ctx = MockContextManager(target_path="os")

    with mock_ctx:
        # Initially no mocks
        assert not mock_ctx.active_mocks

        # Add a function mock
        function_mock = mock_ctx.add_mock("dynamic_function", lambda x: x**2)
        assert os.dynamic_function(3) == 9

        # Add a simple value mock
        value_mock = mock_ctx.add_mock("dynamic_value", 42)
        assert os.dynamic_value == 42

        # Add a dict mock
        dict_mock = mock_ctx.add_mock("dynamic_dict", {"key": "value"})
        assert os.dynamic_dict["key"] == "value"

        # Update an existing mock
        mock_ctx.add_mock("dynamic_function", lambda x: x * 10)
        assert os.dynamic_function(3) == 30
