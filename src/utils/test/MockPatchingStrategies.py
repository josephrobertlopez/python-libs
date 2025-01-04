from unittest.mock import patch, MagicMock
from typing import Mapping

from src.utils.abstract.abstract_strategy import AbstractStrategy


class MethodPatcherStrategy(AbstractStrategy):
    """Strategy for patching methods."""

    def execute(self, *args):
        """Patches a method on the target."""
        if len(args) != 3:
            raise ValueError(
                "MethodPatcherStrategy expects 3 arguments: target_path, name, and behavior."
            )

        target_path, name, behavior = args
        full_path = f"{target_path}.{name}"
        if isinstance(behavior, Mapping):
            mock_method = MagicMock()
            mock_method.__getitem__.side_effect = lambda key: behavior[key]
            mock_method.__setitem__.side_effect = (
                lambda key, value: behavior.__setitem__(key, value)
            )
            mock_method.__contains__.side_effect = lambda key: key in behavior
            patcher = patch(full_path, new=mock_method, create=True)
        elif callable(behavior):
            patcher = patch(full_path, side_effect=behavior, create=True)
        else:
            patcher = patch(full_path, return_value=behavior)
        return patcher


class AttributePatcherStrategy(AbstractStrategy):
    """Strategy for patching attributes."""

    def execute(self, *args):
        """Patches an attribute on the target."""
        if len(args) != 3:
            raise ValueError(
                "AttributePatcherStrategy expects 3 arguments: target_path, name, and value."
            )
        target_path, name, value = args
        full_path = f"{target_path}.{name}"
        # Create a MagicMock and set its return_value if it's not callable or a Mapping
        if callable(value):
            return patch(full_path, side_effect=value, create=True)
        else:
            return patch(full_path, new=value, create=True)


class MappingPatcherStrategy(AbstractStrategy):
    """Strategy for patching dictionary-like objects."""

    def execute(self, *args):
        """Patches a dictionary-like object."""
        if len(args) != 3:
            raise ValueError(
                "MappingPatcherStrategy expects 3 arguments: target_path, name, and behavior."
            )

        target_path, name, behavior = args
        full_path = f"{target_path}.{name}"

        mock_dict = MagicMock()
        mock_dict.__getitem__.side_effect = lambda key: behavior[key]
        mock_dict.__setitem__.side_effect = lambda key, value: behavior.__setitem__(
            key, value
        )
        mock_dict.__contains__.side_effect = lambda key: key in behavior
        patcher = patch(full_path, new=mock_dict, create=True)
        return patcher


class ClassPatcherStrategy(AbstractStrategy):
    """Strategy for patching classes."""

    def execute(self, *args):
        """Patches a class on the target."""
        if len(args) != 3:
            raise ValueError(
                "ClassPatcherStrategy expects 3 arguments: target_path, name, and class_values."
            )

        target_path, name, class_values = args
        full_path = f"{target_path}.{name}"

        # Create a mock class
        mock_class = MagicMock()

        for method_name, return_value in class_values.items():
            # Set each method to return the specified value
            mock_method = MagicMock(return_value=return_value)
            setattr(mock_class, method_name, mock_method)

        # Ensure attributes and methods are on the called instance
        instance_mock = MagicMock()
        for method_name, return_value in class_values.items():
            mock_method = MagicMock(return_value=return_value)
            setattr(instance_mock, method_name, mock_method)

        mock_class.return_value = instance_mock

        patcher = patch(full_path, new=mock_class, create=True)
        return patcher
