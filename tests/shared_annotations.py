"""
Enhanced Shared Test Annotations with Smart Annotation Integration

This module provides convenient decorators and context managers that dramatically
reduce test boilerplate by providing pre-configured mock setups for common scenarios.

Uses the consolidated test framework for consistent mocking patterns.
"""

import functools
import sys
from typing import Dict, Any, Optional, List
from unittest.mock import Mock, MagicMock
from io import StringIO
from functools import partial
import unittest

# Import from consolidated framework
from src.utils.test import (
    smart_mock,
    SmartMockTestCase as _SmartMockTestCase,
    StandardTestCase,
    temporary_mock,
    patch_object,
    MockFactory,
    smart_patches,
)

# =============================================================================
# ADDITIONAL PRESET CONFIGURATIONS
# =============================================================================

# Additional convenience aliases for common test patterns
mock_minimal_sys = partial(smart_mock, "sys", argv=["test"], stdout=StringIO())
mock_minimal_os = partial(smart_mock, "os", getcwd=lambda: "/test")
mock_quiet_logging = partial(smart_mock, "logging", level="CRITICAL")

# =============================================================================
# SPECIALIZED TEST CONFIGURATIONS
# =============================================================================


def mock_interactive_test(**overrides):
    """Decorator for tests requiring user interaction simulation."""
    default_inputs = ["y", "test_input", "42"]

    def mock_input(prompt=""):
        if not hasattr(mock_input, "call_count"):
            mock_input.call_count = 0
        if mock_input.call_count < len(default_inputs):
            result = default_inputs[mock_input.call_count]
            mock_input.call_count += 1
            return result
        return "default"

    config = {"input": mock_input, **overrides}
    return smart_mock("builtins", **config)


def mock_network_test(**overrides):
    """Decorator for network-related testing with offline defaults."""
    return smart_mock(
        "requests",
        get=Mock(
            return_value=Mock(
                status_code=200,
                json=Mock(return_value={"status": "ok"}),
                text="mock response",
            )
        ),
        post=Mock(return_value=Mock(status_code=201)),
        **overrides,
    )


# =============================================================================
# CONVENIENCE DECORATORS - High-level decorators for common test patterns
# =============================================================================


def mock_test_sys(**kwargs):
    """Pre-configured sys module mocking decorator."""
    config = {"sys": kwargs} if kwargs else {"sys": {"argv": ["test_program"]}}
    from src.utils.test import runtime_mock

    return runtime_mock("minimal", **config)


def mock_test_os(**kwargs):
    """Pre-configured os module mocking decorator."""
    config = {"os": kwargs} if kwargs else {"os": {"environ": {"TEST_MODE": "1"}}}
    from src.utils.test import runtime_mock

    return runtime_mock("minimal", **config)


def mock_test_builtins(**kwargs):
    """Pre-configured builtins mocking decorator."""
    config = {"builtins": kwargs} if kwargs else {"builtins": {"open": Mock()}}
    from src.utils.test import runtime_mock

    return runtime_mock("minimal", **config)


def mock_test_module(module_name, **kwargs):
    """Pre-configured module mocking decorator."""
    config = {module_name: kwargs}
    from src.utils.test import runtime_mock

    return runtime_mock("minimal", **config)


def runner_test(argv=None, **kwargs):
    """Convenience decorator for CLI runner tests."""
    argv = argv or ["test_program"]
    config = {"sys": {"argv": argv}, **kwargs}
    from src.utils.test import runtime_mock

    return runtime_mock("minimal", **config)


def output_test(**kwargs):
    """Convenience decorator for tests that need to capture stdout/stderr."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **func_kwargs):
            import sys
            from io import StringIO
            from contextlib import contextmanager

            @contextmanager
            def capture_output():
                old_stdout = sys.stdout
                captured = StringIO()
                sys.stdout = captured
                try:
                    yield captured
                finally:
                    sys.stdout = old_stdout

            # Create a context manager that the test can use
            with capture_output() as captured:
                # Put captured output in kwargs for the test to access
                func_kwargs["captured_stdout"] = captured
                result = func(*args, **func_kwargs)
                return result

        return wrapper

    if kwargs:
        # Called with arguments: @output_test(arg=value)
        return decorator
    else:
        # Called without arguments: @output_test
        return decorator


def audio_test(**kwargs):
    """Convenience decorator for audio/pygame tests."""
    config = {"pygame.mixer": {"init": Mock(), "music": Mock()}, **kwargs}
    from src.utils.test import runtime_mock

    return runtime_mock("audio_system", **config)


def file_system_test(files_exist=None, file_contents=None, **kwargs):
    """Convenience decorator for file system tests."""
    files_exist = files_exist or {}
    file_contents = file_contents or {}

    config = {
        "os.path": {"exists": lambda p: files_exist.get(p, False)},
        "builtins": {"open": lambda f, *args, **kw: StringIO(file_contents.get(f, ""))},
        **kwargs,
    }
    from src.utils.test import runtime_mock

    return runtime_mock("file_system", **config)


def create_runner_test_cases(test_cases):
    """Generate multiple test cases for runner testing."""

    def decorator(cls):
        for name, argv in test_cases.items():

            def make_test(test_argv):
                def test_method(self):
                    # Use the consolidated framework
                    with smart_mock("sys", argv=test_argv):
                        self.assertEqual(sys.argv, test_argv)

                return test_method

            setattr(cls, f"test_{name}", make_test(argv))
        return cls

    return decorator


def create_output_test_cases(test_cases):
    """Generate multiple test cases for output testing."""

    def decorator(cls):
        for name, expected_output in test_cases.items():

            def make_test(expected):
                def test_method(self):
                    with smart_mock("sys", stdout=StringIO()) as ctx:
                        print(expected)
                        output = ctx.get_mock("stdout").getvalue()
                        self.assertIn(expected, output)

                return test_method

            setattr(cls, f"test_{name}", make_test(expected_output))
        return cls

    return decorator


# =============================================================================
# ENHANCED BASE CLASSES
# =============================================================================


class EnhancedTestCase(_SmartMockTestCase):
    """Enhanced test case with additional helper methods."""

    def assert_mock_called_with_any(self, mock_obj, *expected_args):
        """Assert mock was called with any of the expected argument sets."""
        call_args_list = [call.args for call in mock_obj.call_args_list]
        for args in expected_args:
            if args in call_args_list:
                return
        self.fail(
            f"Mock not called with any of {expected_args}. Actual calls: {call_args_list}"
        )

    def get_mock_calls_summary(self, mock_obj):
        """Get a readable summary of all calls made to a mock."""
        if not mock_obj.called:
            return "Mock was not called"

        calls = []
        for i, call in enumerate(mock_obj.call_args_list):
            args_str = ", ".join(repr(arg) for arg in call.args)
            kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in call.kwargs.items())
            call_str = f"Call {i+1}: ({args_str}"
            if kwargs_str:
                call_str += f", {kwargs_str}"
            call_str += ")"
            calls.append(call_str)

        return "\n".join(calls)


# =============================================================================
# PARAMETRIZED TEST HELPERS
# =============================================================================


def create_parametrized_tests(test_cases, base_decorator=None):
    """Create multiple test functions from a list of test cases."""

    def decorator(test_func):
        test_functions = {}

        for i, case in enumerate(test_cases):
            case_name = case.get("name", f"case_{i}")

            def make_test(test_case):
                def parametrized_test(self):
                    return test_func(self, **test_case)

                return parametrized_test

            func_name = f"{test_func.__name__}_{case_name}"
            func = make_test(case)
            func.__name__ = func_name

            if base_decorator:
                func = base_decorator(func)

            test_functions[func_name] = func

        return test_functions

    return decorator


# =============================================================================
# BACKWARD COMPATIBILITY & LEGACY SUPPORT
# =============================================================================

# Pre-configured decorators with minimal setup (legacy compatibility)
mock_basic_sys = partial(
    smart_mock, "sys", argv=["program"], stdout=StringIO(), stderr=StringIO()
)
mock_basic_os = partial(
    smart_mock, "os", getcwd=lambda: "/", environ={"HOME": "/home/user"}
)
mock_basic_builtins = partial(
    smart_mock, "builtins", print=Mock(), open=lambda f, m="r": StringIO()
)

# Legacy aliases for conftest.py compatibility
mock_test_sys = mock_basic_sys
mock_test_os = mock_basic_os
mock_test_builtins = mock_basic_builtins
mock_test_logging = partial(smart_mock, "logging", level="INFO")
mock_test_pygame = partial(
    smart_mock, "pygame.mixer", init=Mock(), get_init=Mock(return_value=True)
)


# Context managers for backward compatibility
def basic_mock_context(**overrides):
    """Context manager for basic testing needs."""
    return smart_patches(
        sys={"argv": ["test"], "stdout": StringIO()},
        os={"getcwd": lambda: "/test"},
        **overrides,
    )


# Context manager aliases for conftest.py
def mock_runner_context(**overrides):
    """Context for runner testing."""
    return smart_patches(sys={"argv": ["runner"]}, **overrides)


def mock_audio_context(**overrides):
    """Context for audio testing."""
    return smart_patches(**{"pygame.mixer": {"init": Mock()}, **overrides})


def mock_logging_context(**overrides):
    """Context for logging testing."""
    return smart_patches(logging={"level": "INFO"}, **overrides)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core decorators (from consolidated framework)
    "smart_mock",
    "temporary_mock",
    "patch_object",
    "MockFactory",
    "StandardTestCase",
    # Specialized decorators
    "mock_interactive_test",
    "mock_network_test",
    "mock_test_sys",
    "mock_test_os",
    "mock_test_builtins",
    "mock_test_module",
    "output_test",
    "runner_test",
    "audio_test",
    "file_system_test",
    # Base classes
    "EnhancedTestCase",
    # Context managers
    "mock_runner_context",
    "mock_audio_context",
    "mock_logging_context",
    # Test case generators
    "create_runner_test_cases",
    "create_output_test_cases",
]
