from contextlib import contextmanager
from unittest.mock import Mock
from src.utils.test.MockPatchingStrategies import (
    AttributePatcherStrategy,
    MappingPatcherStrategy,
    MethodPatcherStrategy, ClassPatcherStrategy,
)


class MockContextManager:
    """
    Manages patching multiple methods, attributes, or dictionary-like objects in a module or class.
    """

    def __init__(
        self,
        target_path,
        method_behaviors=None,
        attribute_values=None,
        mapping_values=None,
        class_values = None,
    ):
        if not isinstance(target_path, str):
            raise TypeError(f"target_path should be a string, got {type(target_path)}")

        self.target_path = target_path
        self.method_behaviors = method_behaviors or {}
        self.attribute_values = attribute_values or {}
        self.mapping_values = mapping_values or {}
        self.class_values = class_values or {}

        self.strategies = {
            "method": MethodPatcherStrategy(),
            "attribute": AttributePatcherStrategy(),
            "mapping": MappingPatcherStrategy(),
            "class": ClassPatcherStrategy(),  # New strategy added here

        }
        self.active_mocks = {}
        self.active_patchers = {}

        self._apply_patches("method", self.method_behaviors)
        self._apply_patches("attribute", self.attribute_values)
        self._apply_patches("mapping", self.mapping_values)
        self._apply_patches("class",self.class_values)


    def _apply_patches(self, patch_type, patch_items):
        """Applies patches using the specified strategy."""
        strategy = self.strategies[patch_type]
        for name, value in patch_items.items():
            patcher = strategy.execute(self.target_path, name, value)
            mock_obj = patcher.start()
            self.active_mocks[name] = mock_obj
            self.active_patchers[name] = patcher

    @contextmanager
    def update_patch(self, name, new_value):
        """Temporarily updates a patch for a specific method, attribute, or dict."""
        if name not in self.active_patchers:
            raise KeyError(f"'{name}' is not patched.")

        old_patcher = self.active_patchers.pop(name)
        self.active_mocks.pop(name)

        old_patcher.stop()

        patch_type = self._get_patch_type(name)
        strategy = self.strategies[patch_type]

        new_patcher = strategy.execute(self.target_path, name, new_value)
        new_mock = new_patcher.start()

        self.active_patchers[name] = new_patcher
        self.active_mocks[name] = new_mock

        try:
            yield new_mock
        finally:
            new_patcher.stop()
            restored_mock = old_patcher.start()
            self.active_patchers[name] = old_patcher
            self.active_mocks[name] = restored_mock

    @contextmanager
    def remove_patch(self, name):
        """Temporarily removes a patch for a method, attribute, or dict."""
        if name not in self.active_patchers:
            raise KeyError(f"'{name}' is not patched.")

        old_patcher = self.active_patchers.pop(name)
        old_patcher.stop()

        mock_obj = self.active_mocks.pop(name)

        try:
            yield mock_obj
        finally:
            new_mock = old_patcher.start()
            self.active_patchers[name] = old_patcher
            self.active_mocks[name] = new_mock

    def _get_patch_type(self, name):
        """Determines the type of patch for a given name."""
        if name in self.method_behaviors:
            return "method"
        if name in self.attribute_values:
            return "attribute"
        if name in self.mapping_values:
            return "mapping"
        if name in self.class_values:
            return "class"

    def get_mock(self, name):
        """Retrieves the mock object for a specific method, attribute, or dict."""
        return self.active_mocks.get(name)

    def __enter__(self):
        """Enters the context, resetting all mocks."""
        for name, mock in self.active_mocks.items():
            if isinstance(mock, Mock):
                mock.reset_mock()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exits the context, stopping all patches."""
        for name, patcher in list(self.active_patchers.items()):
            patcher.stop()
