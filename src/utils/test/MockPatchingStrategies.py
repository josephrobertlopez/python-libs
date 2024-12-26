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
        mock_attr = MagicMock()

        if callable(value):
            mock_attr.side_effect = value
        else:
            mock_attr.return_value = value

        patcher = patch(full_path, new=mock_attr, create=True)
        return patcher


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

import inspect

class ClassPatcherStrategy(AbstractStrategy):
    """Strategy for patching classes and their attributes."""

    def execute(self, *args):
        """Patches a class and its attributes."""
        if len(args) != 3:
            raise ValueError(
                "ClassPatcherStrategy expects 3 arguments: target_path, name, and class."
            )

        target_path, name, class_obj = args
        full_path = f"{target_path}.{name}"

        if not inspect.isclass(class_obj):
            raise TypeError(f"{class_obj} is not a class")

        # Create a mock of the class
        class_mock = MagicMock(spec=class_obj)

        # Iterate over the class attributes and patch inspectable ones
        for attribute_name, attribute_value in class_obj.__dict__.items():
            if not attribute_name.startswith("__"):  # Skip special attributes like __dict__, __module__
                if callable(attribute_value):
                    # If it's callable, set side_effect for methods
                    setattr(class_mock, attribute_name, MagicMock(side_effect=attribute_value))
                else:
                    # Otherwise, set a return_value for attributes
                    setattr(class_mock, attribute_name, MagicMock(return_value=attribute_value))

        patcher = patch(full_path, new=class_mock, create=True)
        return patcher