"""
Base Test Classes and Shared Utilities

This module provides the foundational test classes, utilities, and patterns that
all tests can inherit from or use. It consolidates common test setup patterns,
assertion helpers, and integration with both the runtime annotations and mock
utilities frameworks.

Features:
- Base test classes with runtime mock integration
- Shared assertion helpers and utilities
- Common test patterns and fixtures
- Integration with pytest and unittest
- Environment and configuration management
"""

import os
import sys
import unittest
import pytest
from typing import Any, Dict, List, Optional, Callable, Union
from contextlib import contextmanager
from io import StringIO, BytesIO
from unittest.mock import Mock, MagicMock, patch

# Import our consolidated frameworks
from .runtime_annotations import (
    RuntimeConfig,
    RuntimeContext,
    runtime_mock,
    _ast_analyzer,
    auto_analyze,
    intelligent_preset,
)
from .mock_utilities import smart_mock, smart_patches, MockFactory, MockBuilder


# =============================================================================
# BASE TEST CLASSES
# =============================================================================


class BaseTestCase(unittest.TestCase):
    """Base test case with common utilities and setup patterns."""

    def setUp(self):
        """Common setup for all tests."""
        self.original_sys_modules = sys.modules.copy()
        self.temp_env_vars = {}
        self.cleanup_callbacks = []

    def tearDown(self):
        """Common cleanup for all tests."""
        # Restore environment variables
        for key, original_value in self.temp_env_vars.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value

        # Run cleanup callbacks
        for callback in reversed(self.cleanup_callbacks):
            try:
                callback()
            except Exception:
                pass

        # Restore sys.modules
        sys.modules.clear()
        sys.modules.update(self.original_sys_modules)

    def register_cleanup(self, callback: Callable):
        """Register a cleanup callback."""
        self.cleanup_callbacks.append(callback)

    def set_env_var(self, key: str, value: str):
        """Set an environment variable with automatic cleanup."""
        if key not in self.temp_env_vars:
            self.temp_env_vars[key] = os.environ.get(key)
        os.environ[key] = value

    def unset_env_var(self, key: str):
        """Unset an environment variable with automatic cleanup."""
        if key not in self.temp_env_vars:
            self.temp_env_vars[key] = os.environ.get(key)
        os.environ.pop(key, None)


class SmartMockTestCase(BaseTestCase):
    """Base test case with smart mock integration."""

    def setUp(self):
        """Setup with smart mock capabilities."""
        super().setUp()
        self.mock_contexts = {}
        self.active_patches = []

    def tearDown(self):
        """Cleanup with smart mock teardown."""
        # Clean up mock contexts
        for context in self.mock_contexts.values():
            try:
                context.__exit__(None, None, None)
            except Exception:
                pass

        # Clean up patches
        for patcher in reversed(self.active_patches):
            try:
                patcher.stop()
            except Exception:
                pass

        super().tearDown()

    def create_mock_context(self, name: str, target_path: str, **kwargs):
        """Create a named mock context for reuse."""
        from .mock_utilities import SmartMockContext

        context = SmartMockContext(target_path, **kwargs)
        self.mock_contexts[name] = context
        return context

    def start_mock_context(self, name: str):
        """Start a named mock context."""
        if name in self.mock_contexts:
            return self.mock_contexts[name].__enter__()
        return None

    def stop_mock_context(self, name: str):
        """Stop a named mock context."""
        if name in self.mock_contexts:
            try:
                self.mock_contexts[name].__exit__(None, None, None)
            except Exception:
                pass

    @contextmanager
    def mock_module(self, module_path: str, **kwargs):
        """Context manager for temporary module mocking."""
        with smart_mock(module_path, **kwargs) as context:
            yield context

    def patch_method(self, target: str, mock_value: Any):
        """Patch a method with automatic cleanup."""
        patcher = patch(target, mock_value)
        mock_obj = patcher.start()
        self.active_patches.append(patcher)
        return mock_obj


class RuntimeTestCase(SmartMockTestCase):
    """Base test case with runtime annotation integration."""

    def setUp(self):
        """Setup with runtime annotation support."""
        super().setUp()
        self.runtime_config = RuntimeConfig({})  # Start with empty config
        self.runtime_contexts = {}

    def tearDown(self):
        """Cleanup runtime contexts."""
        for context in self.runtime_contexts.values():
            try:
                context.__exit__(None, None, None)
            except Exception:
                pass
        super().tearDown()

    def apply_runtime_preset(self, preset_name: str, **overrides):
        """Apply a runtime preset configuration."""
        config = RuntimeConfig(preset_name, **overrides)
        context = RuntimeContext(config)
        self.runtime_contexts[preset_name] = context
        return context.__enter__()

    def apply_runtime_template(
        self, template_name: str, variables: Optional[Dict] = None, **overrides
    ):
        """Apply a runtime template configuration."""
        config = RuntimeConfig(template_name, **(variables or {}), **overrides)
        context = RuntimeContext(config)
        context_id = f"template_{template_name}"
        self.runtime_contexts[context_id] = context
        return context.__enter__()

    def create_custom_runtime_config(self, **modules):
        """Create a custom runtime configuration."""
        context = RuntimeContext(modules)
        context_id = f"custom_{id(context)}"
        self.runtime_contexts[context_id] = context
        return context.__enter__()


class ParametrizedTestCase(RuntimeTestCase):
    """Base test case with parametrized test generation support."""

    @classmethod
    def generate_test_cases(
        cls, test_name: str, parameters: List[Dict[str, Any]], test_method: Callable
    ):
        """Generate parametrized test cases dynamically."""
        for i, params in enumerate(parameters):
            test_case_name = f"{test_name}_{i}"

            def create_test_method(params_dict):
                def test_method_wrapper(self):
                    return test_method(self, **params_dict)

                return test_method_wrapper

            setattr(cls, test_case_name, create_test_method(params))

    @classmethod
    def create_test_matrix(
        cls,
        test_name: str,
        parameter_matrix: Dict[str, List[Any]],
        test_method: Callable,
    ):
        """Create a test matrix from parameter combinations."""
        import itertools

        keys = list(parameter_matrix.keys())
        values = list(parameter_matrix.values())

        parameters = []
        for combination in itertools.product(*values):
            params = dict(zip(keys, combination))
            parameters.append(params)

        cls.generate_test_cases(test_name, parameters, test_method)


class SmartTestCase(unittest.TestCase):
    """
    AST-enhanced test base class with intelligent configuration.

    This class provides automatic test analysis and configuration using AST.
    It detects patterns in your test methods and automatically applies optimal
    mock configurations, reducing boilerplate by up to 90%.

    Features:
    - Automatic AST analysis of test methods
    - Intelligent preset selection
    - Auto-generated mock configurations
    - Pattern detection (CLI, logging, file ops, etc.)
    - Complexity analysis and optimization suggestions
    """

    def setUp(self):
        """Set up AST analysis and intelligent configuration."""
        super().setUp()
        self._ast_analyzer = _ast_analyzer
        self._auto_configs = {}
        self._detected_patterns = set()

    def tearDown(self):
        """Clean up AST analysis resources."""
        super().tearDown()
        self._auto_configs.clear()
        self._detected_patterns.clear()

    def analyze_test_method(self, method_name: str = None) -> Dict[str, Any]:
        """
        Analyze a test method using AST to detect patterns and requirements.

        Args:
            method_name: Name of method to analyze (defaults to current test)

        Returns:
            Dict containing analysis results with patterns, imports, calls, etc.
        """
        if method_name is None:
            # Get the current test method name
            method_name = self._testMethodName

        method = getattr(self, method_name, None)
        if method is None:
            return {}

        return self._ast_analyzer.analyze_function(method)

    def apply_intelligent_preset(
        self, preset_name: str = None, **overrides
    ) -> RuntimeContext:
        """
        Apply an intelligent preset with AST validation.

        If no preset is specified, uses AST analysis to recommend the best one.

        Args:
            preset_name: Preset to apply (None for auto-detection)
            **overrides: Additional configuration overrides

        Returns:
            RuntimeContext that can be used as context manager
        """
        if preset_name is None:
            analysis = self.analyze_test_method()
            preset_name = analysis.get("recommended_preset", "minimal")

        config = RuntimeConfig(preset_name, **overrides)
        return RuntimeContext(config)

    def auto_mock_setup(self, enable_warnings: bool = True) -> RuntimeContext:
        """
        Automatically set up mocks based on AST analysis of the current test.

        Args:
            enable_warnings: Whether to show optimization warnings

        Returns:
            RuntimeContext with auto-generated mocks
        """
        analysis = self.analyze_test_method()

        if enable_warnings and analysis.get("complexity_score", 1) > 5:
            print(
                f"⚠️  High complexity test detected (score: {analysis['complexity_score']}). Consider breaking into smaller tests."
            )

        auto_mocks = analysis.get("auto_mocks", {})
        if auto_mocks:
            return RuntimeContext(auto_mocks)
        else:
            return RuntimeContext({})

    def get_pattern_suggestions(self) -> List[str]:
        """
        Get suggestions for improving the current test based on AST analysis.

        Returns:
            List of optimization suggestions
        """
        analysis = self.analyze_test_method()
        suggestions = []

        patterns = analysis.get("patterns", set())
        recommended_preset = analysis.get("recommended_preset", "minimal")
        complexity = analysis.get("complexity_score", 1)

        if complexity > 3:
            suggestions.append(
                f"Consider breaking this test into smaller methods (complexity: {complexity})"
            )

        if len(patterns) > 2:
            suggestions.append(
                f"Multiple patterns detected: {', '.join(patterns)}. Consider using '{recommended_preset}' preset."
            )

        if "logging_system" in patterns and "file_operations" in patterns:
            suggestions.append(
                "Use @intelligent_preset('logging_system') for optimal logging + file operation mocking"
            )

        return suggestions

    @contextmanager
    def smart_context(self, auto_analyze: bool = True, **manual_overrides):
        """
        Intelligent context manager that combines AST analysis with manual overrides.

        Args:
            auto_analyze: Whether to perform automatic AST analysis
            **manual_overrides: Manual mock configurations (take precedence)
        """
        if auto_analyze:
            auto_config = self.auto_mock_setup(enable_warnings=False)
            with auto_config as auto_ctx:
                if manual_overrides:
                    manual_config = RuntimeContext(manual_overrides)
                    with manual_config as manual_ctx:
                        yield {"auto": auto_ctx, "manual": manual_ctx}
                else:
                    yield {"auto": auto_ctx, "manual": None}
        else:
            if manual_overrides:
                manual_config = RuntimeContext(manual_overrides)
                with manual_config as manual_ctx:
                    yield {"auto": None, "manual": manual_ctx}
            else:
                yield {"auto": None, "manual": None}

    def quick_analysis(self) -> str:
        """
        Get a quick summary of AST analysis for the current test.

        Returns:
            Human-readable analysis summary
        """
        analysis = self.analyze_test_method()

        patterns = analysis.get("patterns", set())
        recommended = analysis.get("recommended_preset", "minimal")
        complexity = analysis.get("complexity_score", 1)
        imports = analysis.get("imports", set())
        auto_mocks = analysis.get("auto_mocks", {})

        summary = f"""
🔍 AST Analysis Summary for {self._testMethodName}:
   📋 Detected Patterns: {', '.join(patterns) if patterns else 'None'}
   🎯 Recommended Preset: {recommended}
   📊 Complexity Score: {complexity}/10
   📦 Key Imports: {', '.join(list(imports)[:5])}{'...' if len(imports) > 5 else ''}
   🤖 Auto-Mocks Available: {len(auto_mocks) if isinstance(auto_mocks, dict) else 0}
        """.strip()

        return summary


# =============================================================================
# PYTEST INTEGRATION
# =============================================================================


class PytestBase:
    """Base class for pytest-style tests with our framework integration."""

    def setup_method(self, method):
        """Setup for pytest methods."""
        self.mock_contexts = {}
        self.cleanup_callbacks = []
        self.temp_env_vars = {}

    def teardown_method(self, method):
        """Teardown for pytest methods."""
        # Clean up mock contexts
        for context in self.mock_contexts.values():
            try:
                context.__exit__(None, None, None)
            except Exception:
                pass

        # Restore environment variables
        for key, original_value in self.temp_env_vars.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value

        # Run cleanup callbacks
        for callback in reversed(self.cleanup_callbacks):
            try:
                callback()
            except Exception:
                pass

    def register_cleanup(self, callback: Callable):
        """Register a cleanup callback."""
        self.cleanup_callbacks.append(callback)

    def set_env_var(self, key: str, value: str):
        """Set environment variable with cleanup."""
        if key not in self.temp_env_vars:
            self.temp_env_vars[key] = os.environ.get(key)
        os.environ[key] = value

    @contextmanager
    def runtime_preset(self, preset_name: str, **overrides):
        """Runtime preset context manager for pytest."""
        config = RuntimeConfig(preset_name, **overrides)
        with RuntimeContext(config) as context:
            yield context

    @contextmanager
    def smart_mock_context(self, module_path: str, **kwargs):
        """Smart mock context manager for pytest."""
        with smart_mock(module_path, **kwargs) as context:
            yield context


# =============================================================================
# ASSERTION HELPERS
# =============================================================================


class AssertionHelpers:
    """Collection of custom assertion helpers."""

    @staticmethod
    def assert_mock_called_with_pattern(mock_obj: Mock, *args, **kwargs):
        """Assert mock was called with arguments matching patterns."""
        if not mock_obj.called:
            raise AssertionError(f"Mock {mock_obj} was not called")

        for call in mock_obj.call_args_list:
            call_args, call_kwargs = call
            if (len(args) == 0 or call_args == args) and (
                len(kwargs) == 0
                or all(call_kwargs.get(k) == v for k, v in kwargs.items())
            ):
                return True

        raise AssertionError(f"Mock {mock_obj} was not called with expected arguments")

    @staticmethod
    def assert_output_contains(
        captured_output: str, expected_text: str, case_sensitive: bool = True
    ):
        """Assert that captured output contains expected text."""
        if not case_sensitive:
            captured_output = captured_output.lower()
            expected_text = expected_text.lower()

        if expected_text not in captured_output:
            raise AssertionError(
                f"Expected '{expected_text}' not found in output: '{captured_output}'"
            )

    @staticmethod
    def assert_file_operation(operation: str, filepath: str, mock_open: Mock):
        """Assert that a file operation was performed."""
        if operation == "read":
            mock_open.assert_called_with(filepath, "r")
        elif operation == "write":
            mock_open.assert_called_with(filepath, "w")
        elif operation == "append":
            mock_open.assert_called_with(filepath, "a")
        else:
            # Check if file was opened with the specified operation
            mock_open.assert_called()

    @staticmethod
    def assert_environment_variable(key: str, expected_value: Optional[str] = None):
        """Assert environment variable state."""
        if expected_value is None:
            if key in os.environ:
                raise AssertionError(f"Environment variable '{key}' should not be set")
        else:
            actual_value = os.environ.get(key)
            if actual_value != expected_value:
                raise AssertionError(
                    f"Environment variable '{key}' expected '{expected_value}', got '{actual_value}'"
                )


# =============================================================================
# COMMON TEST FIXTURES
# =============================================================================


class CommonFixtures:
    """Collection of common test fixtures and data."""

    @staticmethod
    def sample_sys_argv(
        program_name: str = "test_program", args: Optional[List[str]] = None
    ):
        """Generate sample sys.argv configuration."""
        args = args or ["--verbose", "--output", "test.txt"]
        return [program_name] + args

    @staticmethod
    def sample_os_environ(base_vars: Optional[Dict[str, str]] = None):
        """Generate sample os.environ configuration."""
        env_vars = {
            "TEST_MODE": "true",
            "DEBUG": "false",
            "CONFIG_PATH": "/test/config",
            "LOG_LEVEL": "INFO",
        }
        if base_vars:
            env_vars.update(base_vars)
        return env_vars

    @staticmethod
    def sample_file_contents():
        """Generate sample file contents for mocking."""
        return {
            "config.txt": "test_setting=value\ndebug=true",
            "data.json": '{"key": "value", "number": 42}',
            "log.txt": "INFO: Test started\nERROR: Test error\nINFO: Test completed",
            "empty.txt": "",
            "binary.dat": b"\x00\x01\x02\x03",
        }

    @staticmethod
    def sample_network_responses():
        """Generate sample network response configurations."""
        return {
            "GET": {
                "status_code": 200,
                "json_data": {"success": True, "data": ["item1", "item2"]},
                "text": "Success response",
            },
            "POST": {
                "status_code": 201,
                "json_data": {"created": True, "id": 123},
                "text": "Created",
            },
            "PUT": {
                "status_code": 200,
                "json_data": {"updated": True},
                "text": "Updated",
            },
            "DELETE": {"status_code": 204, "text": ""},
        }


# =============================================================================
# TEST UTILITIES AND HELPERS
# =============================================================================


class TestUtilities:
    """Collection of test utility functions."""

    @staticmethod
    def capture_stdout():
        """Create StringIO for capturing stdout."""
        return StringIO()

    @staticmethod
    def capture_stderr():
        """Create StringIO for capturing stderr."""
        return StringIO()

    @staticmethod
    def create_temp_file_mock(content: str = "test content", mode: str = "r"):
        """Create a temporary file mock."""
        return MockFactory.create_file_mock(content, mode)

    @staticmethod
    def create_mock_builder():
        """Create a mock builder for complex configurations."""
        return MockBuilder()

    @staticmethod
    @contextmanager
    def isolated_filesystem():
        """Context manager for isolated filesystem operations."""
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()

        try:
            os.chdir(temp_dir)
            yield temp_dir
        finally:
            os.chdir(original_cwd)
            shutil.rmtree(temp_dir, ignore_errors=True)

    @staticmethod
    def create_test_logger():
        """Create a test logger with captured output."""
        import logging

        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.DEBUG)

        # Remove existing handlers
        logger.handlers.clear()

        # Add string handler for capturing
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger, log_capture


# =============================================================================
# INTEGRATION MIXINS
# =============================================================================


class RuntimeMockMixin:
    """Mixin for runtime mock integration."""

    def use_runtime_preset(self, preset_name: str, **overrides):
        """Decorator factory for runtime preset usage."""

        def decorator(test_method):
            @functools.wraps(test_method)
            def wrapper(*args, **kwargs):
                config = RuntimeConfig(preset_name, **overrides)
                with RuntimeContext(config):
                    return test_method(*args, **kwargs)

            return wrapper

        return decorator

    def use_smart_mocks(self, **module_configs):
        """Decorator factory for smart mock usage."""

        def decorator(test_method):
            @functools.wraps(test_method)
            def wrapper(*args, **kwargs):
                with smart_patches(**module_configs):
                    return test_method(*args, **kwargs)

            return wrapper

        return decorator


class AssertionMixin(AssertionHelpers):
    """Mixin providing assertion helpers to test classes."""

    pass


class FixtureMixin(CommonFixtures, TestUtilities):
    """Mixin providing fixtures and utilities to test classes."""

    pass


# =============================================================================
# COMPLETE TEST BASE CLASSES
# =============================================================================


class StandardTestCase(RuntimeTestCase, AssertionMixin, FixtureMixin, RuntimeMockMixin):
    """Complete test case with all framework features."""

    pass


class StandardPytestBase(PytestBase, AssertionMixin, FixtureMixin, RuntimeMockMixin):
    """Complete pytest base with all framework features."""

    pass


# =============================================================================
# BACKWARD COMPATIBILITY ALIASES
# =============================================================================

# Legacy class names from the original files
BaseSmartTest = SmartMockTestCase
MockTestCase = SmartMockTestCase

# Export commonly used items
__all__ = [
    # Base classes
    "BaseTestCase",
    "SmartMockTestCase",
    "RuntimeTestCase",
    "ParametrizedTestCase",
    "PytestBase",
    "StandardTestCase",
    "StandardPytestBase",
    "SmartTestCase",
    # Mixins
    "RuntimeMockMixin",
    "AssertionMixin",
    "FixtureMixin",
    # Utilities
    "AssertionHelpers",
    "CommonFixtures",
    "TestUtilities",
    # Legacy compatibility
    "BaseSmartTest",
    "MockTestCase",
]
