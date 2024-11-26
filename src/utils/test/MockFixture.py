from unittest.mock import patch


class MockFixture:
    """
    Manages patching multiple methods and attributes in a module or class.

    Attributes:
        mock_path: Path to the module or class to patch.
        default_behaviors: Dict of method names to return values or side effects.
        default_attributes: Dict of attribute names and their mocked values.
        mocks: Dict of created mock objects, keyed by method or attribute name.
        patchers: Dict of patcher objects for managing teardown.
    """

    def __init__(self, mock_path, default_behaviors=None, default_attributes=None):
        """
        Initializes MockFixture to mock specified methods and attributes.

        Args:
            mock_path: Base path of the module or class to patch.
            default_behaviors: Optional dict of method names and
                their return values or side effects.
            default_attributes: Optional dict of attribute names and
                their mocked values.
        """
        if not isinstance(mock_path, str):
            raise TypeError(f"mock_path should be a string, got {type(mock_path)}")

        self.mock_path = mock_path
        self.default_behaviors = default_behaviors or {}
        self.default_attributes = default_attributes or {}
        self.mocks = {}
        self.patchers = {}

        try:
            self._patch_methods()
            self._patch_attributes()
        except Exception as e:
            raise RuntimeError(f"Error while patching: {e}")

    def _patch_methods(self):
        """Patches each method in `default_behaviors`."""
        for method_name, return_value in self.default_behaviors.items():
            full_path = f"{self.mock_path}.{method_name}"

            try:
                if not callable(return_value):
                    patcher = patch(full_path, return_value=return_value, autospec=True)
                else:
                    patcher = patch(full_path, side_effect=return_value, create=True)

                mock_obj = patcher.start()
                self.mocks[method_name] = mock_obj
                self.patchers[method_name] = patcher
            except Exception as e:
                raise ValueError(f"Failed to patch {full_path}: {e}")

    def _patch_attributes(self):
        """Patches each attribute in `default_attributes`."""
        for attr_name, value in self.default_attributes.items():
            full_path = f"{self.mock_path}.{attr_name}"

            try:
                patcher = patch(full_path, new=value, create=True)
                mock_obj = patcher.start()
                self.mocks[attr_name] = mock_obj
                self.patchers[attr_name] = patcher
            except Exception as e:
                raise ValueError(f"Failed to patch {full_path}: {e}")

    def update_patch(self, name, value):
        """
        Updates the patch for a specific method or attribute.

        Args:
            name: Name of the method or attribute to update.
            value: New return value, side effect, or attribute value.

        Raises:
            KeyError: If the method or attribute has not been patched.
        """
        if name not in self.mocks:
            raise KeyError(f"'{name}' is not patched.")

        try:
            if callable(value):
                self.mocks[name].return_value = value
                self.mocks[name].side_effect = None
            else:
                self.mocks[name].return_value = None
                self.mocks[name].side_effect = value
        except AttributeError:
            patcher = self.patchers[name]
            patcher.stop()
            full_path = f"{self.mock_path}.{name}"
            patcher = patch(full_path, new=value, create=True)
            self.patchers[name] = patcher
            self.mocks[name] = patcher.start()
        except Exception as e:
            raise ValueError(f"Failed to update patch for '{name}': {e}")

    def remove_patch(self, name):
        """
        Removes the patch for a specific method or attribute.

        Args:
            name: Name of the method or attribute to remove the patch for.

        Raises:
            KeyError: If the method or attribute has not been patched.
        """
        if name not in self.mocks:
            raise KeyError(f"'{name}' is not patched.")

        try:
            self.mocks.pop(name)
            patcher = self.patchers.pop(name)
            patcher.stop()
        except Exception as e:
            raise ValueError(f"Failed to remove patch for '{name}': {e}")

    def get_mock_obj(self, name):
        """
        Retrieves the mock object for a specific method or attribute.

        Args:
            name: Name of the method or attribute to retrieve.

        Returns:
            Mock object if patched, else None.
        """
        return self.mocks.get(name)

    def __enter__(self):
        """Enters the context, returning the MockFixture instance."""
        for mock in self.mocks.values():
            mock.reset_mock()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exits the context, stopping all mocks."""
        for patcher in self.patchers.values():
            patcher.stop()
