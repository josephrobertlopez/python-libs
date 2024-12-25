from unittest.mock import MagicMock

import pytest

from src.utils.test.MockPatchingStrategies import (
    AttributePatcherStrategy,
    MappingPatcherStrategy,
    MethodPatcherStrategy,
    AbstractStrategy,
)


def test_method_patcher(mock_context):
    """Test the MethodPatcherStrategy."""
    strategy = MethodPatcherStrategy()
    patcher = strategy.execute(
        mock_context["target_path"], "method_name", lambda x: x + 1
    )
    mock_method = patcher.start()

    assert callable(mock_method)
    assert mock_method(2) == 3  # Testing the side_effect

    patcher.stop()


def test_attribute_patcher(mock_context):
    """Test the AttributePatcherStrategy."""
    strategy = AttributePatcherStrategy()
    mock_attr = MagicMock()
    mock_attr.__getitem__.return_value = 5
    patcher = strategy.execute(mock_context["target_path"], "attr_name", mock_attr)
    patcher.start()

    assert mock_attr["attr_name"] == 5  # Testing the mock behavior
    patcher.stop()


def test_mapping_patcher(mock_context):
    """Test the MappingPatcherStrategy."""
    strategy = MappingPatcherStrategy()
    mock_dict = {"key": "value"}
    patcher = strategy.execute(mock_context["target_path"], "map_name", mock_dict)
    patcher.start()

    assert mock_dict["key"] == "value"  # Testing mock dict behavior
    patcher.stop()
