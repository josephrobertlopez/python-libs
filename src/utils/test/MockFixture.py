class MockFixture:
    """
    Manages patching multiple methods in a module or class using pytest-mock.

    Attributes:
        mocker: The pytest-mock mocker fixture.
        mock_path: Path to the module or class to patch.
        default_behaviors: Dict of method names to return
            values or side effects.
        mocks: Dict of created mock objects, keyed by method name.
    """

    def __init__(self, mocker: object,
                 mock_path: object,
                 default_behaviors: object = None) -> object:
        """
        Initializes MockFixture to mock specified methods.

        Args:
            mocker: pytest-mock's mocker fixture for patching.
            mock_path: Base path of the module or class to patch.
            default_behaviors: Optional dict of method names and
                their return values or side effects.
        """
        self.mocker = mocker
        self.mock_path = mock_path
        self.default_behaviors = default_behaviors or {}
        self.mocks = {}
        self._patch_methods()

    def _patch_methods(self):
        """Patches each method in `default_behaviors` with the g
            iven return value or side effect."""
        for method_name, return_value in self.default_behaviors.items():
            full_path = f"{self.mock_path}.{method_name}"
            patcher = self.mocker.patch(full_path, autospec=True)
            if callable(return_value):
                patcher.side_effect = return_value
            else:
                patcher.return_value = return_value
            self.mocks[method_name] = patcher

    def get_mock_obj(self, method_name):
        """
        Retrieves the mock object for a specific method.

        Args:
            method_name: Name of the method to retrieve.

        Returns:
            Mock object if patched, else None.
        """
        return self.mocks.get(method_name)

    def __enter__(self):
        """Enters the context, returning the MockFixture instance."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exits the context."""
        pass
