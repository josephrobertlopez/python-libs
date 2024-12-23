import pytest
from unittest.mock import MagicMock

from src.utils.test.MockContextManager import MockContextManager
from src.utils.test.MockPatchingStrategies import (
    AttributePatcherStrategy,
    MappingPatcherStrategy,
    MethodPatcherStrategy,
)


@pytest.fixture
def mock_context():
    """Fixture to set up common mock context for tests."""
    return {
        "target_path": "tests.utils.test.test_mockcontextmanager",
        "method_behaviors": {"method_name": lambda x: x * 2},
        "attribute_values": {"attr_name": 42},
        "mapping_values": {"map_name": {"key": "value"}},
    }


def test_method_patcher(mock_context):
    """Test the MethodPatcherStrategy."""
    strategy = MethodPatcherStrategy()
    patcher = strategy.patch(
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
    patcher = strategy.patch(mock_context["target_path"], "attr_name", mock_attr)
    patcher.start()

    assert mock_attr["attr_name"] == 5  # Testing the mock behavior
    patcher.stop()


def test_mapping_patcher(mock_context):
    """Test the MappingPatcherStrategy."""
    strategy = MappingPatcherStrategy()
    mock_dict = {"key": "value"}
    patcher = strategy.patch(mock_context["target_path"], "map_name", mock_dict)
    patcher.start()

    assert mock_dict["key"] == "value"  # Testing mock dict behavior
    patcher.stop()


def test_mock_context_manager(mock_context):
    """Test the MockContextManager with method, attribute, and mapping patches."""
    with MockContextManager(
        mock_context["target_path"],
        mock_context["method_behaviors"],
        mock_context["attribute_values"],
        mock_context["mapping_values"],
    ) as context:
        mock_method = context.get_mock("method_name")
        mock_attr = context.get_mock("attr_name")
        mock_map = context.get_mock("map_name")

        assert mock_method is not None
        assert mock_attr is not None
        assert mock_map is not None

        mock_method.side_effect = lambda x: x + 10
        assert mock_method(5) == 15

        mock_attr.__getitem__.side_effect = lambda key: 100
        assert mock_attr["attr_name"] == 100

        mock_map.__getitem__.side_effect = lambda key: "new_value"
        assert mock_map["key"] == "new_value"


def test_update_patch(mock_context):
    """Test the update_patch method of MockContextManager."""
    with MockContextManager(
        mock_context["target_path"],
        mock_context["method_behaviors"],
        mock_context["attribute_values"],
    ) as context:
        with context.update_patch("method_name", lambda x: x * 3) as new_mock:
            assert new_mock(4) == 12  # Testing the updated patch


def test_remove_patch(mock_context):
    """Test the remove_patch method of MockContextManager."""
    with MockContextManager(
        mock_context["target_path"],
        mock_context["method_behaviors"],
        mock_context["attribute_values"],
    ) as context:
        with context.remove_patch("method_name"):
            assert "method_name" not in context.active_patchers
