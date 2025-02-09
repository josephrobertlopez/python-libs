import pytest

from src.utils.test.mock_context_manager import MockContextManager


def test_mock_context_manager(mock_context):
    """Test the MockContextManager with method, attribute, and mapping patches."""
    # Happy Path
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

        assert mock_attr == 42

        mock_map.__getitem__.side_effect = lambda key: "new_value"
        assert mock_map["key"] == "new_value"

    # Negative Path
    mock_context["target_path"] = None
    with pytest.raises(TypeError, match="target_path should be a string"):
        MockContextManager(
            mock_context["target_path"],
            mock_context["method_behaviors"],
            mock_context["attribute_values"],
            mock_context["mapping_values"],
        )


def test_update_patch(mock_context):
    """Test the update_patch method of MockContextManager."""
    with MockContextManager(
        mock_context["target_path"],
        mock_context["method_behaviors"],
        mock_context["attribute_values"],
        mock_context["mapping_values"],
    ) as context:
        with context.update_patch("method_name", lambda x: x * 3) as new_mock:
            assert new_mock(4) == 12  # Testing the updated patch
        with context.update_patch("attr_name", 420) as new_mock:
            assert new_mock == 420
        with context.update_patch("map_name", {}) as new_mock:
            assert new_mock
        with pytest.raises(KeyError, match="is not patched."):
            with context.update_patch("not_patched_method", lambda x: x + 3):
                pass


def test_remove_patch(mock_context):
    """Test the remove_patch method of MockContextManager."""
    with MockContextManager(
        mock_context["target_path"],
        mock_context["method_behaviors"],
        mock_context["attribute_values"],
        mock_context["mapping_values"],
    ) as context:
        with context.remove_patch("method_name"):
            assert "method_name" not in context.active_patchers
        with pytest.raises(KeyError, match="is not patched."):
            with context.remove_patch("not_patched_method"):
                pass
