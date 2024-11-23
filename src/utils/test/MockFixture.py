from unittest.mock import patch


class MockFixture:
    """
    Manages patching multiple methods in a module or class.

    Attributes:
        mock_path: Path to the module or class to patch.
        default_behaviors: Dict of method names to return
            values or side effects.
        mocks: Dict of created mock objects, keyed by method name.
        patchers: Dict of patcher objects for managing teardown.
    """

    def __init__(self, mock_path, default_behaviors=None):
        """
        Initializes MockFixture to mock specified methods.

        Args:
            mock_path: Base path of the module or class to patch.
            default_behaviors: Optional dict of method names and
                their return values or side effects.
        """
        self.mock_path = mock_path
        self.default_behaviors = default_behaviors or {}
        self.mocks = {}
        self.patchers = {}
        self._patch_methods()

    def _patch_methods(self):
        """Patches each method in `default_behaviors`."""
        for method_name, return_value in self.default_behaviors.items():
            full_path = f"{self.mock_path}.{method_name}"

            if callable(return_value):
                patcher = patch(full_path, return_value=return_value, autospec=True)
            else:
                patcher = patch(full_path, side_effect=return_value, create=True)

            mock_obj = patcher.start()
            # Store mock objects and patchers for later use
            self.mocks[method_name] = mock_obj
            self.patchers[method_name] = patcher

    def update_patch(self,method_name,return_value):
        if callable(return_value):
            self.mocks[method_name].return_value = return_value
            self.mocks[method_name].side_effect = None
        else:
            self.mocks[method_name].return_value = None
            self.mocks[method_name].side_effect = None

    def remove_patch(self,method_name):
        mock = self.mocks.pop(method_name)
        patcher = self.patchers.pop(method_name)
        patcher.stop()

    def get_mock_obj(self, method_name):
        """
        Retrieves the mock object for a specific method.

        Args:
            method_name: Name of the method to retrieve.

        Returns:
            Mock object if patched, else None.
        """
        return self.mocks.get(method_name)

    def reset_mocks(self):
        """Stop all patchers and clear the patchers/mocks."""
        for mock in self.mocks.values():
            mock.reset_mock()

    def __enter__(self):
        """Enters the context, returning the MockFixture instance."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exits the context, stopping all mocks."""
        for patcher in self.patchers.values():
            patcher.stop()
