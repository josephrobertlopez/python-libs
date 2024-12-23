from unittest.mock import patch, MagicMock
from typing import Mapping


class PatcherStrategy:
    """Base class for all patching strategies."""

    def patch(self, target_path, name, value):
        raise NotImplementedError


class MethodPatcherStrategy(PatcherStrategy):
    """Strategy for patching methods."""

    def patch(self, target_path, name, behavior):
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


class AttributePatcherStrategy(PatcherStrategy):
    """Strategy for patching attributes."""

    def patch(self, target_path, name, value):
        full_path = f"{target_path}.{name}"

        # Create a MagicMock and set its return_value if it's not callable or a Mapping
        mock_attr = MagicMock()

        # If the behavior (value) is a callable, it will be used as the side effect
        if callable(value):
            mock_attr.side_effect = value
        else:
            mock_attr.return_value = value

        # Patch the attribute with the mock object
        patcher = patch(full_path, new=mock_attr, create=True)

        return patcher


class MappingPatcherStrategy(PatcherStrategy):
    """Strategy for patching dictionary-like objects."""

    def patch(self, target_path, name, behavior):
        full_path = f"{target_path}.{name}"

        mock_dict = MagicMock()
        mock_dict.__getitem__.side_effect = lambda key: behavior[key]
        mock_dict.__setitem__.side_effect = lambda key, value: behavior.__setitem__(
            key, value
        )
        mock_dict.__contains__.side_effect = lambda key: key in behavior
        patcher = patch(full_path, new=mock_dict, create=True)

        return patcher
