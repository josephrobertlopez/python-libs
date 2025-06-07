import inspect
from collections.abc import Mapping, Collection
from typing import Any, Callable, Dict, Optional, Union
from unittest.mock import patch, MagicMock

from src.utils.abstract.abstract_strategy import AbstractStrategy


class MethodPatcherStrategy(AbstractStrategy):
    """Strategy for patching methods or callables."""

    def execute(self, *args) -> Any:
        """Create a patcher for a method.

        Args:
            args: Should contain (target_path, method_name, method_behavior)

        Returns:
            unittest.mock.patch object
        """
        if len(args) != 3:
            raise ValueError(
                "MethodPatcherStrategy expects 3 arguments: target_path, method_name, "
                "and method_behavior."
            )

        target_path, method_name, method_behavior = args
        full_path = f"{target_path}.{method_name}"

        # Use create=True to allow patching of non-existent methods
        if callable(method_behavior):
            # Create a MagicMock with side_effect for callables
            mock = MagicMock()
            mock.side_effect = method_behavior
            return patch(full_path, mock, create=True)
        else:
            return patch(full_path, method_behavior, create=True)


class AttributePatcherStrategy(AbstractStrategy):
    """Strategy for patching attributes."""

    def execute(self, *args) -> Any:
        """Create a patcher for an attribute.

        Args:
            args: Should contain (target_path, attribute_name, attribute_value)

        Returns:
            unittest.mock.patch object
        """
        if len(args) != 3:
            raise ValueError(
                "AttributePatcherStrategy expects 3 arguments: target_path, "
                "attribute_name, and attribute_value."
            )

        target_path, attribute_name, attribute_value = args
        full_path = f"{target_path}.{attribute_name}"
        # Use create=True to allow patching of non-existent attributes
        return patch(full_path, attribute_value, create=True)


class MappingPatcherStrategy(AbstractStrategy):
    """Strategy for patching mappings like dictionaries."""

    def execute(self, *args) -> Any:
        """Create a patcher for a mapping.

        Args:
            args: Should contain (target_path, mapping_name, mapping_values)

        Returns:
            unittest.mock.patch object
        """
        if len(args) != 3:
            raise ValueError(
                "MappingPatcherStrategy expects 3 arguments: target_path, mapping_name, "
                "and mapping_values."
            )

        target_path, mapping_name, mapping_values = args
        full_path = f"{target_path}.{mapping_name}"

        # Create a mock that behaves like a mapping
        mock_mapping = MagicMock()

        # If we're given an actual mapping, configure the mock to use its values
        if isinstance(mapping_values, Mapping):
            # Set up __getitem__ to return values from the mapping
            mock_mapping.__getitem__.side_effect = lambda key: mapping_values.get(key)
            # Make it act like a real mapping
            mock_mapping.items.return_value = mapping_values.items()
            mock_mapping.keys.return_value = mapping_values.keys()
            mock_mapping.values.return_value = mapping_values.values()
            mock_mapping.__iter__.return_value = iter(mapping_values)
            mock_mapping.__contains__.side_effect = lambda key: key in mapping_values

        # Use create=True to allow patching of non-existent mappings
        return patch(full_path, mock_mapping, create=True)


class ClassPatcherStrategy(AbstractStrategy):
    """Strategy for patching classes."""

    def execute(self, *args) -> Any:
        """Create a patcher for a class.

        Args:
            args: Should contain (target_path, class_name, class_methods)

        Returns:
            unittest.mock.patch object
        """
        if len(args) != 3:
            raise ValueError(
                "ClassPatcherStrategy expects 3 arguments: target_path, class_name, "
                "and class_methods."
            )

        target_path, class_name, class_methods = args
        full_path = f"{target_path}.{class_name}"

        # Create a class mock with appropriate methods
        mock_class = MagicMock()
        instance_mock = MagicMock()

        # Configure the instance mock with the provided methods
        if isinstance(class_methods, dict):
            for method_name, return_value in class_methods.items():
                method_mock = MagicMock(return_value=return_value)
                setattr(instance_mock, method_name, method_mock)

        # Make the class return our configured instance
        mock_class.return_value = instance_mock

        # Use create=True to allow patching of non-existent classes
        return patch(full_path, mock_class, create=True)


class SmartPatcherStrategy(AbstractStrategy):
    """Strategy that automatically detects the type of input and uses the appropriate strategy.

    This strategy will automatically detect the type of input and use the appropriate strategy:
    - For callable objects (functions, methods, etc.), it will use MethodPatcherStrategy
    - For class objects, it will create a class mock that returns instance mocks
    - For mappings (dict, etc.), it will use MappingPatcherStrategy
    - For collections (list, tuple, set), it will patch directly
    - For all other objects, it will use AttributePatcherStrategy
    """

    def execute(self, *args) -> Any:
        if len(args) != 3:
            raise ValueError(
                "SmartPatcherStrategy expects 3 arguments: target_path, name, and behavior."
            )
        target_path, name, behavior = args
        full_path = f"{target_path}.{name}"

        try:
            # Handle callable but not class (functions, methods, etc.)
            if callable(behavior) and not isinstance(behavior, type):
                mock = MagicMock()
                mock.side_effect = behavior
                return patch(full_path, mock, create=True)

            # Handle class objects
            elif isinstance(behavior, type):
                class_mock = MagicMock()
                instance_mock = MagicMock()
                try:
                    # Try to create an instance of the class to inspect its methods
                    instance = behavior()
                    for method_name, method in inspect.getmembers(
                        instance, inspect.ismethod
                    ):
                        if not method_name.startswith("__"):
                            try:
                                # Try to get the return value of the method
                                original_return = method()
                                method_mock = MagicMock(return_value=original_return)
                            except Exception:
                                # If the method call fails, just create a basic mock
                                method_mock = MagicMock()
                            setattr(instance_mock, method_name, method_mock)
                except Exception:
                    # If we can't create an instance, proceed with just the class mock
                    pass
                class_mock.return_value = instance_mock
                return patch(full_path, class_mock, create=True)

            # Handle mapping objects (dict, etc.)
            elif isinstance(behavior, Mapping):
                mapping_strategy = MappingPatcherStrategy()
                return mapping_strategy.execute(target_path, name, behavior)

            # Handle collection objects (list, tuple, set, etc.)
            elif isinstance(behavior, Collection) and not isinstance(
                behavior, (str, bytes, bytearray)
            ):
                return patch(full_path, behavior, create=True)

            # Handle everything else as a simple value
            else:
                return patch(full_path, behavior, create=True)

        except Exception as e:
            # Fallback to a simple patch if anything goes wrong
            print(
                f"Warning: Error in SmartPatcherStrategy for {full_path}: {str(e)}. Falling back to simple patch."
            )
            return patch(full_path, MagicMock(), create=True)
