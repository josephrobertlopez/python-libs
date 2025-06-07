import sys
from unittest.mock import MagicMock

from src.utils.test.mock_patching_strategies import (
    AttributePatcherStrategy,
    ClassPatcherStrategy,
    MappingPatcherStrategy,
    MethodPatcherStrategy,
    SmartPatcherStrategy,
)


class SampleClass:
    def method(self):
        return "original"


def test_method_patcher(mock_context):
    """Test the MethodPatcherStrategy."""
    strategy = MethodPatcherStrategy()
    patcher = strategy.execute(
        mock_context["target_path"], "method_name", lambda x: x + 1
    )
    mock_method = patcher.start()

    try:
        assert callable(mock_method)
        assert mock_method(2) == 3  # Testing the side_effect
    finally:
        patcher.stop()


def test_method_patcher_with_mapping(mock_context):
    """Test the MethodPatcherStrategy with mapping behavior."""
    strategy = MethodPatcherStrategy()
    behavior = {"key1": "value1", "key2": "value2"}
    patcher = strategy.execute(mock_context["target_path"], "method_name", behavior)
    mock_method = patcher.start()

    try:
        # With the updated implementation, a mapping is now directly patched (not as a callable)
        assert mock_method == behavior
        assert mock_method["key1"] == "value1"
        assert mock_method["key2"] == "value2"
        assert "key1" in mock_method
        assert "nonexistent" not in mock_method
    finally:
        patcher.stop()


def test_attribute_patcher(mock_context):
    """Test the AttributePatcherStrategy."""
    strategy = AttributePatcherStrategy()
    patcher = strategy.execute(mock_context["target_path"], "attr_name", 42)
    mock_attr = patcher.start()

    try:
        assert mock_attr == 42
    finally:
        patcher.stop()


def test_mapping_patcher(mock_context):
    """Test the MappingPatcherStrategy."""
    strategy = MappingPatcherStrategy()
    mapping = {"a": 1, "b": 2, "c": 3}
    patcher = strategy.execute(mock_context["target_path"], "mapping_name", mapping)
    mock_mapping = patcher.start()

    try:
        assert mock_mapping["a"] == 1
        assert mock_mapping["b"] == 2
        assert mock_mapping["c"] == 3
        assert "a" in mock_mapping
        assert "z" not in mock_mapping
    finally:
        patcher.stop()


def test_class_patcher(mock_context):
    """Test the ClassPatcherStrategy."""
    strategy = ClassPatcherStrategy()
    class_values = {"method1": "result1", "method2": 42}
    patcher = strategy.execute(mock_context["target_path"], "class_name", class_values)
    mock_class = patcher.start()

    try:
        # Test the class methods
        instance = mock_class()
        assert instance.method1() == "result1"
        assert instance.method2() == 42
    finally:
        patcher.stop()


def test_smart_patcher_simple(mock_context):
    """Test the SmartPatcherStrategy with different types of inputs."""
    strategy = SmartPatcherStrategy()

    # Test with a callable
    callable_patcher = strategy.execute(
        mock_context["target_path"], "func", lambda x: x * 2
    )
    mock_func = callable_patcher.start()

    try:
        assert callable(mock_func)
        assert mock_func(5) == 10
    finally:
        callable_patcher.stop()

    # Test with a value
    value_patcher = strategy.execute(mock_context["target_path"], "value", 42)
    mock_value = value_patcher.start()

    try:
        assert mock_value == 42
    finally:
        value_patcher.stop()

    # Test with a dict
    dict_patcher = strategy.execute(
        mock_context["target_path"], "config", {"key": "value"}
    )
    mock_dict = dict_patcher.start()

    try:
        assert mock_dict["key"] == "value"
        assert "key" in mock_dict
    finally:
        dict_patcher.stop()


def test_smart_patcher_with_class(mock_context):
    """Test the SmartPatcherStrategy with a class."""
    strategy = SmartPatcherStrategy()
    class_patcher = strategy.execute(
        mock_context["target_path"], "TestClass", SampleClass
    )
    mock_class = class_patcher.start()

    try:
        instance = mock_class()
        assert instance.method() == "original"
    finally:
        class_patcher.stop()
