from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional, Type, Union
from unittest.mock import patch, Mock, MagicMock

from src.utils.test.mock_context_manager import MockContextManager


@contextmanager
def smart_mock(target_path: str, **kwargs) -> MockContextManager:
    """A smart context manager for mocking that automatically detects input types.

    This context manager wraps MockContextManager with the auto_mock parameter,
    allowing it to automatically detect and apply the appropriate mocking strategy
    based on the type of each mock value.

    Args:
        target_path: The import path to the target module or object
        **kwargs: Keyword arguments where each key is the name of something to mock
                  and the value is the mock behavior/value.

    Yields:
        MockContextManager: The active mock context, which can be used to
                           add/update mocks during the test.

    Examples:
        >>> with smart_mock("my_module", func=lambda x: x*2, value=42):
        ...     result = my_module.func(21)  # Returns 42
        ...     assert my_module.value == 42
    """
    mock_context = MockContextManager(target_path=target_path, auto_mock=kwargs)
    with mock_context:
        yield mock_context


def patch_object(obj: Any, attr_name: str, mock_value: Any) -> Any:
    """A smart patching utility for patching attributes on objects.

    This function detects the type of mock_value and applies the appropriate
    patching approach. It is a simpler, more targeted version of patch.object.

    Args:
        obj: The object to patch
        attr_name: The name of the attribute/method to patch
        mock_value: The mock value or behavior to apply

    Returns:
        A context manager that patches the object attribute

    Examples:
        >>> with patch_object(my_obj, "method", lambda x: x*2):
        ...     result = my_obj.method(21)  # Returns 42
    """
    # We use a direct mock with side_effect for callable behavior
    if callable(mock_value) and not isinstance(mock_value, type):
        return patch.object(obj, attr_name, side_effect=mock_value)
    else:
        # For non-callables, use a direct value replacement
        return patch.object(obj, attr_name, mock_value)


def create_mock_class(
    class_methods: Optional[Dict[str, Any]] = None,
    class_attributes: Optional[Dict[str, Any]] = None,
) -> Type:
    """Create a mock class with specified methods and attributes.

    This utility creates a mock class type that can be instantiated and will
    behave according to the specified methods and attributes.

    Args:
        class_methods: Dictionary of method names to return values or callables
        class_attributes: Dictionary of attribute names to values

    Returns:
        A mock class type that can be instantiated

    Examples:
        >>> MockDB = create_mock_class(
        ...     class_methods={"query": lambda: [{"id": 1}]},
        ...     class_attributes={"connection_string": "mock://db"}
        ... )
        >>> db = MockDB()
        >>> db.query()  # Returns [{"id": 1}]
        >>> db.connection_string  # Returns "mock://db"
    """
    class_methods = class_methods or {}
    class_attributes = class_attributes or {}

    # Create a new class that will be the mock
    class MockClass:
        def __init__(self):
            # Add all attributes to the instance
            for name, value in class_attributes.items():
                setattr(self, name, value)

    # Add all methods to the class
    for method_name, behavior in class_methods.items():
        if callable(behavior):
            # For callables, create a bound method
            # Check if the callable expects 'self' as first parameter
            import inspect

            try:
                sig = inspect.signature(behavior)
                params = list(sig.parameters.keys())
                if params and params[0] == "self":
                    # Already has self parameter, use directly
                    setattr(MockClass, method_name, behavior)
                else:
                    # Wrap to add self parameter
                    def make_instance_method(func):
                        def instance_method(self, *args, **kwargs):
                            return func(*args, **kwargs)

                        return instance_method

                    setattr(MockClass, method_name, make_instance_method(behavior))
            except (ValueError, TypeError):
                # If we can't inspect the signature, assume it needs self
                setattr(MockClass, method_name, behavior)
        else:
            # For non-callables, create a method that returns the value
            def make_method(return_value):
                def method(self, *args, **kwargs):
                    return return_value

                return method

            setattr(MockClass, method_name, make_method(behavior))

    return MockClass
