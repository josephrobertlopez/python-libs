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

        try:
            if isinstance(behavior, Mapping):
                mock_method = MagicMock()
                mock_method.__getitem__.side_effect = lambda key: behavior[key]
                mock_method.__setitem__.side_effect = lambda key, value: behavior.__setitem__(key, value)
                mock_method.__contains__.side_effect = lambda key: key in behavior
                patcher = patch(full_path, new=mock_method, create=True)
            elif callable(behavior):
                patcher = patch(full_path, side_effect=behavior, create=True)
            else:
                patcher = patch(full_path, return_value=behavior, autospec=True)

            return patcher
        except Exception as e:
            raise ValueError(f"Failed to patch {full_path}: {e}")


class AttributePatcherStrategy(PatcherStrategy):
    """Strategy for patching attributes."""

    def patch(self, target_path, name, value):
        full_path = f"{target_path}.{name}"

        try:
            if isinstance(value, Mapping):
                mock_attr = MagicMock()
                mock_attr.__getitem__.side_effect = lambda key: value[key]
                mock_attr.__setitem__.side_effect = lambda key, value_: value.__setitem__(key, value_)
                mock_attr.__contains__.side_effect = lambda key: key in value
                patcher = patch(full_path, new=mock_attr, create=True)
            else:
                patcher = patch(full_path, new=value, create=True)

            return patcher
        except Exception as e:
            raise ValueError(f"Failed to patch {full_path}: {e}")

class MappingPatcherStrategy(PatcherStrategy):
    """Strategy for patching dictionary-like objects."""

    def patch(self, target_path, name, behavior):
        full_path = f"{target_path}.{name}"

        try:
            mock_dict = MagicMock()
            mock_dict.__getitem__.side_effect = lambda key: behavior[key]
            mock_dict.__setitem__.side_effect = lambda key, value: behavior.__setitem__(key, value)
            mock_dict.__contains__.side_effect = lambda key: key in behavior
            patcher = patch(full_path, new=mock_dict, create=True)

            return patcher
        except Exception as e:
            raise ValueError(f"Failed to patch {full_path}: {e}")
