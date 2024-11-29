from unittest.mock import patch


class MockManager:
    """
    Manages patching multiple methods and attributes in a module or class.

    Attributes:
        target_path: Path to the module or class to patch.
        method_behaviors: Dict of method names to return values or side effects.
        attribute_values: Dict of attribute names and their mocked values.
        active_mocks: Dict of created mock objects, keyed by method or attribute name.
        active_patchers: Dict of patcher objects for managing teardown.
    """

    def __init__(self, target_path, method_behaviors=None, attribute_values=None):
        """
        Initializes MockManager to mock specified methods and attributes.

        Args:
            target_path: Base path of the module or class to patch.
            method_behaviors: Optional dict of method names and
                their return values or side effects.
            attribute_values: Optional dict of attribute names and
                their mocked values.
        """
        if not isinstance(target_path, str):
            raise TypeError(f"target_path should be a string, got {type(target_path)}")

        self.target_path = target_path
        self.method_behaviors = method_behaviors or {}
        self.attribute_values = attribute_values or {}
        self.active_mocks = {}
        self.active_patchers = {}

        try:
            self._patch_methods()
            self._patch_attributes()
        except Exception as e:
            raise RuntimeError(f"Error while patching: {e}")

    def _patch_methods(self):
        """Patches each method in `method_behaviors`."""
        for method_name, behavior in self.method_behaviors.items():
            full_path = f"{self.target_path}.{method_name}"

            try:
                if not callable(behavior):
                    patcher = patch(full_path, return_value=behavior, autospec=True)
                else:
                    patcher = patch(full_path, side_effect=behavior, create=True)

                mock_obj = patcher.start()
                self.active_mocks[method_name] = mock_obj
                self.active_patchers[method_name] = patcher
            except Exception as e:
                raise ValueError(f"Failed to patch {full_path}: {e}")

    def _patch_attributes(self):
        """Patches each attribute in `attribute_values`."""
        for attr_name, value in self.attribute_values.items():
            full_path = f"{self.target_path}.{attr_name}"

            try:
                patcher = patch(full_path, new=value, create=True)
                mock_obj = patcher.start()
                self.active_mocks[attr_name] = mock_obj
                self.active_patchers[attr_name] = patcher
            except Exception as e:
                raise ValueError(f"Failed to patch {full_path}: {e}")

    def update_patch(self, name, new_value):
        """
        Updates the patch for a specific method or attribute.

        Args:
            name: Name of the method or attribute to update.
            new_value: New return value, side effect, or attribute value.

        Raises:
            KeyError: If the method or attribute has not been patched.
        """
        if name not in self.active_mocks:
            raise KeyError(f"'{name}' is not patched.")

        try:
            if callable(new_value):
                self.active_mocks[name].side_effect = new_value
                self.active_mocks[name].return_value = None
            else:
                self.active_mocks[name].return_value = new_value
                self.active_mocks[name].side_effect = None
        except AttributeError:
            patcher = self.active_patchers[name]
            patcher.stop()
            full_path = f"{self.target_path}.{name}"
            patcher = patch(full_path, new=new_value, create=True)
            self.active_patchers[name] = patcher
            self.active_mocks[name] = patcher.start()
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
        if name not in self.active_mocks:
            raise KeyError(f"'{name}' is not patched.")

        try:
            self.active_mocks.pop(name)
            patcher = self.active_patchers.pop(name)
            patcher.stop()
        except Exception as e:
            raise ValueError(f"Failed to remove patch for '{name}': {e}")

    def get_mock(self, name):
        """
        Retrieves the mock object for a specific method or attribute.

        Args:
            name: Name of the method or attribute to retrieve.

        Returns:
            Mock object if patched, else None.
        """
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
