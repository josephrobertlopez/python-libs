from typing import Mapping
from src.utils.test.MockStrategies import MethodPatcherStrategy, AttributePatcherStrategy, MappingPatcherStrategy
from contextlib import contextmanager

class MockManager:
    """
    Manages patching multiple methods, attributes, or dictionary-like objects in a module or class.
    """
    def __init__(self, target_path, method_behaviors=None, attribute_values=None):
        """
        Initializes MockManager to mock specified methods, attributes, and dictionary-like objects.
        """
        if not isinstance(target_path, str):
            raise TypeError(f"target_path should be a string, got {type(target_path)}")

        self.target_path = target_path
        self.method_behaviors = method_behaviors or {}
        self.attribute_values = attribute_values or {}
        self.active_mocks = {}
        self.active_patchers = {}

        self._patch_methods()
        self._patch_attributes()

    def _patch_methods(self):
        """Patches each method in `method_behaviors`."""
        method_strategy = MethodPatcherStrategy()
        for method_name, behavior in self.method_behaviors.items():
            patcher = method_strategy.patch(self.target_path, method_name, behavior)
            mock_obj = patcher.start()
            self.active_mocks[method_name] = mock_obj
            self.active_patchers[method_name] = patcher

    def _patch_attributes(self):
        """Patches each attribute in `attribute_values`."""
        attribute_strategy = AttributePatcherStrategy()
        for attr_name, value in self.attribute_values.items():
            patcher = attribute_strategy.patch(self.target_path, attr_name, value)
            mock_obj = patcher.start()
            self.active_mocks[attr_name] = mock_obj
            self.active_patchers[attr_name] = patcher
    @contextmanager
    def update_patch(self, name, new_value):
        """Updates the patch for a specific method, attribute, or dict."""
        if name in self.method_behaviors:
            patcher_strategy = MethodPatcherStrategy()
        elif name in self.attribute_values:
            patcher_strategy = AttributePatcherStrategy()
        else:
            raise KeyError(f"'{name}' is not patched.")

        patcher = self.active_patchers[name]
        patcher.stop()  # Stop the current patch
        new_patcher = patcher_strategy.patch(self.target_path, name, new_value)
        new_mock_obj = new_patcher.start()  # Start the new patch
        self.active_patchers[name] = new_patcher  # Update patcher
        self.active_mocks[name] = new_mock_obj  # Update mock
        self.method_behaviors[name] = new_value  # Update stored behavior

        yield new_mock_obj  # Yield the new mock object to be used in the context

    @contextmanager
    def remove_patch(self, name):
        """Removes the patch for a specific method, attribute, or dict."""
        if name not in self.active_mocks:
            raise KeyError(f"'{name}' is not patched.")

        patcher = self.active_patchers.pop(name)
        patcher.stop()
        self.active_mocks.pop(name)

        yield  # Yield to allow for cleanup within the context

    def get_mock(self, name):
        """Retrieves the mock object for a specific method, attribute, or dict."""
        return self.active_mocks.get(name)

    def __enter__(self):
        """Enters the context, resetting all mocks."""
        for mock in self.active_mocks.values():
            mock.reset_mock()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exits the context, stopping all mocks."""
        for patcher in self.active_patchers.values():
            patcher.stop()