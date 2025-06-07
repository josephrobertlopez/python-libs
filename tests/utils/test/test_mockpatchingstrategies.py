from unittest.mock import MagicMock, patch

from src.utils.test.mock_patching_strategies import (
    AttributePatcherStrategy,
    ClassPatcherStrategy,
    MappingPatcherStrategy,
    MethodPatcherStrategy,
)


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
        assert mock_method["key1"] == "value1"
        assert mock_method["key2"] == "value2"
        assert "key1" in mock_method
        assert "nonexistent" not in mock_method
    finally:
        patcher.stop()


def test_attribute_patcher(mock_context):
    """Test the AttributePatcherStrategy."""
    strategy = AttributePatcherStrategy()
    mock_attr = MagicMock()
    mock_attr.__getitem__.return_value = 5
    patcher = strategy.execute(mock_context["target_path"], "attr_name", mock_attr)
    
    try:
        patcher.start()
        assert mock_attr["attr_name"] == 5  # Testing the mock behavior
    finally:
        patcher.stop()


def test_mapping_patcher(mock_context):
    """Test the MappingPatcherStrategy."""
    strategy = MappingPatcherStrategy()
    mock_dict = {"key": "value", "another_key": 42}
    patcher = strategy.execute(mock_context["target_path"], "map_name", mock_dict)
    
    try:
        patcher.start()
        assert mock_dict["key"] == "value"  # Testing mock dict behavior
        assert mock_dict["another_key"] == 42
        assert "key" in mock_dict
        assert "nonexistent" not in mock_dict
    finally:
        patcher.stop()


def test_class_patcher(mock_context):
    """Test the ClassPatcherStrategy."""
    strategy = ClassPatcherStrategy()
    class_values = {"method1": "return1", "method2": 42}
    patcher = strategy.execute(mock_context["target_path"], "TestClass", class_values)
    
    try:
        mock_class = patcher.start()
        # Test the class methods directly
        assert mock_class.method1() == "return1"
        assert mock_class.method2() == 42
        
        # Test the instance methods
        instance = mock_class()
        assert instance.method1() == "return1"
        assert instance.method2() == 42
    finally:
        patcher.stop()
