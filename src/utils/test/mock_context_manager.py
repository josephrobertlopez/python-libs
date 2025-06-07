from typing import Any, Dict, List, Optional, Union, MutableMapping
from unittest.mock import patch, MagicMock

from src.utils.test.mock_patching_strategies import (
    AttributePatcherStrategy,
    ClassPatcherStrategy,
    MappingPatcherStrategy,
    MethodPatcherStrategy,
    SmartPatcherStrategy,
)


class MockContextManager:
    """A context manager for handling multiple patches.

    This class provides a way to manage multiple patches within a context block.
    It supports different patching strategies and allows for dynamically adding,
    updating, and removing mocks during runtime.

    Attributes:
        target_path: The import path to the target module or class
        active_patchers: A dictionary of active patchers
        active_mocks: A dictionary of active mock objects
        strategies: A dictionary of strategy objects for different mock types
    """

    def __init__(
        self,
        target_path: str,
        method_behaviors: Optional[Dict[str, Any]] = None,
        attribute_values: Optional[Dict[str, Any]] = None,
        mapping_values: Optional[Dict[str, MutableMapping]] = None,
        class_values: Optional[Dict[str, Dict[str, Any]]] = None,
        auto_mock: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the MockContextManager.

        Args:
            target_path: The import path to the target module or class
            method_behaviors: A dictionary of method names to mock behaviors
            attribute_values: A dictionary of attribute names to mock values
            mapping_values: A dictionary of mapping names to mock dictionaries
            class_values: A dictionary of class names to mock class configurations
            auto_mock: A dictionary of names to mock with auto-detected strategy

        Raises:
            TypeError: If target_path is not a string or any of the dictionaries are not of the expected type
        """
        # Validate inputs
        if not isinstance(target_path, str):
            raise TypeError("target_path should be a string")

        if method_behaviors is not None and not isinstance(method_behaviors, dict):
            raise TypeError("method_behaviors should be a dictionary")

        if attribute_values is not None and not isinstance(attribute_values, dict):
            raise TypeError("attribute_values should be a dictionary")

        if mapping_values is not None and not isinstance(mapping_values, dict):
            raise TypeError("mapping_values should be a dictionary")

        if class_values is not None and not isinstance(class_values, dict):
            raise TypeError("class_values should be a dictionary")

        if auto_mock is not None and not isinstance(auto_mock, dict):
            raise TypeError("auto_mock should be a dictionary")

        self.target_path = target_path
        self.active_patchers = {}
        self.active_mocks = {}

        # Initialize strategies
        self.strategies = {
            "method": MethodPatcherStrategy(),
            "attribute": AttributePatcherStrategy(),
            "mapping": MappingPatcherStrategy(),
            "class": ClassPatcherStrategy(),
            "auto": SmartPatcherStrategy(),
        }

        # Store the values to mock
        self.method_behaviors = method_behaviors or {}
        self.attribute_values = attribute_values or {}
        self.mapping_values = mapping_values or {}
        self.class_values = class_values or {}
        self.auto_mock_values = auto_mock or {}

    def _apply_patches(self, patch_type: str, patch_items: Dict[str, Any]) -> None:
        """Applies patches using the specified strategy."""
        strategy = self.strategies[patch_type]
        for name, value in patch_items.items():
            try:
                patcher = strategy.execute(self.target_path, name, value)
                mock_obj = patcher.start()
                self.active_mocks[name] = mock_obj
                self.active_patchers[name] = patcher
            except Exception as e:
                raise RuntimeError(
                    f"Error patching {name} with {patch_type} strategy: {str(e)}"
                )

    def apply_all_patches(self) -> None:
        """Apply all patches using their respective strategies."""
        # Apply method patches
        if self.method_behaviors:
            self._apply_patches("method", self.method_behaviors)

        # Apply attribute patches
        if self.attribute_values:
            self._apply_patches("attribute", self.attribute_values)

        # Apply mapping patches
        if self.mapping_values:
            self._apply_patches("mapping", self.mapping_values)

        # Apply class patches
        if self.class_values:
            self._apply_patches("class", self.class_values)

        # Apply auto-detected patches
        if self.auto_mock_values:
            self._apply_patches("auto", self.auto_mock_values)

    def remove_all_patches(self) -> None:
        """Remove all active patches."""
        errors = []
        # Create a copy of the keys to avoid mutation during iteration
        patcher_names = list(self.active_patchers.keys())

        for name in patcher_names:
            try:
                patcher = self.active_patchers[name]
                patcher.stop()
            except Exception as e:
                errors.append(f"Error stopping patcher for {name}: {str(e)}")

        self.active_patchers.clear()
        self.active_mocks.clear()

        if errors:
            # Log errors but don't raise to ensure all patchers are stopped
            import sys
            sys.stdout.write(f"Errors occurred while stopping patchers: {', '.join(errors)}\n")
            sys.stdout.flush()

    def __enter__(self):
        """Enter the context manager and apply all patches."""
        self.apply_all_patches()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and remove all patches."""
        try:
            self.remove_all_patches()
        except Exception as e:
            # Log the error but don't mask the original exception
            import sys
            sys.stdout.write(f"Error during cleanup in MockContextManager.__exit__: {str(e)}\n")
            sys.stdout.flush()
        # Don't suppress exceptions from the with block
        return False

    def add_mock(self, name: str, behavior: Any) -> Any:
        """Add a new mock or update an existing one during runtime.

        Args:
            name: The name of the attribute/method to mock
            behavior: The behavior to use for mocking

        Returns:
            The mock object

        Examples:
            >>> with MockContextManager("my_module") as mock_ctx:
            ...     # Add a new mock during runtime
            ...     mock_ctx.add_mock("new_function", lambda x: x*2)
            ...     result = my_module.new_function(5)  # Returns 10
        """
        # Check if we already have a mock with this name
        if name in self.active_patchers:
            # Stop the existing patcher before replacing it
            try:
                self.active_patchers[name].stop()
            except Exception as e:
                import sys
                sys.stdout.write(f"Warning: Error stopping existing patcher for {name}: {str(e)}\n")
                sys.stdout.flush()

        # Use the auto-detect strategy for any type of behavior
        try:
            strategy = self.strategies["auto"]
            patcher = strategy.execute(self.target_path, name, behavior)
            mock_obj = patcher.start()

            # Update our tracking dictionaries
            self.active_mocks[name] = mock_obj
            self.active_patchers[name] = patcher

            return mock_obj
        except Exception as e:
            raise RuntimeError(f"Error adding mock for {name}: {str(e)}")

    def get_mock(self, name: str) -> Any:
        """Get a mock object by name.

        Args:
            name: The name of the mock to retrieve

        Returns:
            The mock object

        Raises:
            KeyError: If the mock does not exist
        """
        if name not in self.active_mocks:
            raise KeyError(f"No mock named '{name}' exists")
        return self.active_mocks[name]

    def update_patch(self, name: str, new_behavior: Any):
        """Update an existing patch with a new behavior.

        This method returns a context manager that temporarily updates a patch
        and restores it when exiting the context.

        Args:
            name: The name of the patch to update
            new_behavior: The new behavior to use

        Returns:
            A context manager for the temporary update

        Examples:
            >>> with mock_ctx.update_patch("function", lambda x: x*3):
            ...     # Original function temporarily modified
            ...     result = my_module.function(5)  # Returns 15
            # Original behavior is restored after the context
        """
        return _TempPatchUpdate(self, name, new_behavior)

    def remove_patch(self, name: str):
        """Remove a patch temporarily.

        This method returns a context manager that temporarily removes a patch
        and restores it when exiting the context.

        Args:
            name: The name of the patch to remove

        Returns:
            A context manager for the temporary removal

        Examples:
            >>> with mock_ctx.remove_patch("function"):
            ...     # Original function is used
            ...     result = my_module.function(5)
            # Mock is restored after the context
        """
        return _TempPatchRemoval(self, name)


class _TempPatchUpdate:
    """A context manager for temporarily updating a patch."""

    def __init__(self, mock_context: MockContextManager, name: str, new_behavior: Any):
        self.mock_context = mock_context
        self.name = name
        self.new_behavior = new_behavior
        self.old_behavior = None
        self.old_patcher = None

    def __enter__(self):
        # Check if the mock exists
        if self.name not in self.mock_context.active_patchers:
            raise KeyError(f"Mock '{self.name}' is not patched.")

        # Save the old patcher and behavior
        self.old_patcher = self.mock_context.active_patchers[self.name]
        self.old_patcher.stop()

        # Create a new patch
        strategy = self.mock_context.strategies["auto"]
        patcher = strategy.execute(
            self.mock_context.target_path, self.name, self.new_behavior
        )
        mock_obj = patcher.start()
        self.mock_context.active_mocks[self.name] = mock_obj
        self.mock_context.active_patchers[self.name] = patcher
        return mock_obj

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Remove the temporary patch
        if self.name in self.mock_context.active_patchers:
            self.mock_context.active_patchers[self.name].stop()

        # Restore the original patch if it existed
        if self.old_patcher:
            mock_obj = self.old_patcher.start()
            self.mock_context.active_mocks[self.name] = mock_obj
            self.mock_context.active_patchers[self.name] = self.old_patcher


class _TempPatchRemoval:
    """A context manager for temporarily removing a patch."""

    def __init__(self, mock_context: MockContextManager, name: str):
        self.mock_context = mock_context
        self.name = name
        self.old_patcher = None

    def __enter__(self):
        # Check if the mock exists
        if self.name not in self.mock_context.active_patchers:
            raise KeyError(f"Mock '{self.name}' is not patched.")

        # Save and remove the old patch
        self.old_patcher = self.mock_context.active_patchers[self.name]
        self.old_patcher.stop()
        del self.mock_context.active_patchers[self.name]
        del self.mock_context.active_mocks[self.name]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore the original patch if it existed
        if self.old_patcher:
            mock_obj = self.old_patcher.start()
            self.mock_context.active_mocks[self.name] = mock_obj
            self.mock_context.active_patchers[self.name] = self.old_patcher
