"""
Unified Mock Framework Tests

This single test file demonstrates all patterns using the config-driven
factory approach with annotations and contexts.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os
from io import StringIO

# Import unified framework components
from src.utils.test import runtime_mock, runtime_context, StandardTestCase, smart_mock


class TestUnifiedMockFramework(StandardTestCase):
    """Test the unified mock framework with config-driven approaches."""

    def test_basic_decorator_pattern(self):
        """Test basic decorator using factory-generated config."""

        @runtime_mock("minimal", sys={"argv": ["unified_test"]})
        def test_function():
            return sys.argv

        result = test_function()
        self.assertEqual(result, ["unified_test"])

    def test_context_manager_pattern(self):
        """Test context manager with config-driven approach."""
        config = {"sys": {"argv": ["test_app"]}}

        with runtime_context(config):
            self.assertEqual(sys.argv, ["test_app"])

    @runtime_mock("minimal", sys={"stdout": StringIO()})
    def test_output_capture_annotation(self):
        """Test output capture using annotation factory."""
        print("test output")
        self.assertIsInstance(sys.stdout, StringIO)

    @runtime_mock("minimal", sys={"argv": ["factory_test"]})
    def test_runner_annotation_factory(self):
        """Test runner using pre-configured factory annotation."""
        self.assertEqual(sys.argv, ["factory_test"])

    def test_composed_context_managers(self):
        """Test composition of multiple context managers."""
        sys_config = {"sys": {"argv": ["composed"], "executable": "test_exe"}}
        os_config = {"os": {"getcwd": lambda: "/test/dir"}}

        with runtime_context(sys_config):
            with runtime_context(os_config):
                self.assertEqual(sys.argv, ["composed"])
                self.assertEqual(os.getcwd(), "/test/dir")

    def test_factory_generated_mocks(self):
        """Test using factory-generated mock configurations."""
        # Use pre-defined config from factory
        file_config = {"exists": lambda p: p.endswith(".txt")}

        with runtime_context({"os.path": file_config}):
            self.assertTrue(os.path.exists("/input.txt"))

    def test_annotation_stacking(self):
        """Test stacking multiple factory-generated annotations."""

        @runtime_mock("minimal", sys={"argv": ["stacked"]})
        @runtime_mock("minimal", sys={"stdout": StringIO()})
        def stacked_test():
            print("test")
            return sys.argv[0]

        result = stacked_test()
        self.assertEqual(result, "stacked")


class TestConfigDrivenPatterns(StandardTestCase):
    """Test config-driven patterns using the unified factory approach."""

    def setUp(self):
        """Set up common config patterns."""
        super().setUp()
        self.common_configs = {
            "test_runner": {
                "sys": {"argv": ["runner"], "stdout": StringIO()},
                "os": {"getcwd": lambda: "/runner/dir"},
            },
            "file_handler": {
                "os.path": {"exists": lambda p: p.endswith(".txt")},
                "builtins": {"open": lambda f, m="r": StringIO("mock content")},
            },
        }

    def test_config_driven_sys_mocking(self):
        """Test system mocking using config factory."""
        config = self.common_configs["test_runner"]["sys"]

        with runtime_context({"sys": config}):
            self.assertEqual(sys.argv, ["runner"])
            self.assertIsInstance(sys.stdout, StringIO)

    def test_config_driven_file_mocking(self):
        """Test file operations using config factory."""
        config = self.common_configs["file_handler"]

        with runtime_context(config):
            self.assertTrue(os.path.exists("test.txt"))
            self.assertFalse(os.path.exists("test.py"))

            with open("any_file.txt") as f:
                content = f.read()
                self.assertEqual(content, "mock content")

    def test_nested_config_contexts(self):
        """Test nested contexts using config-driven approach."""
        configs = [
            {"sys": {"argv": ["nested1"]}},
            {"os": {"getcwd": lambda: "/nested"}},
        ]

        def apply_configs(configs):
            if not configs:
                return sys.argv + [os.getcwd()]

            config = configs[0]
            with runtime_context(config):
                return apply_configs(configs[1:])

        result = apply_configs(configs)
        self.assertEqual(result, ["nested1", "/nested"])


class TestFactoryAnnotationPatterns(StandardTestCase):
    """Test factory-generated annotation patterns."""

    def test_pre_configured_system_mocks(self):
        """Test pre-configured system mocks from factory."""

        @runtime_mock(
            "minimal",
            sys={
                "argv": ["program_name"],
                "executable": "fake_executable_path",
                "frozen": True,
            },
        )
        def system_test():
            return {
                "argv": sys.argv,
                "executable": sys.executable,
                "frozen": getattr(sys, "frozen", False),
            }

        result = system_test()
        self.assertEqual(result["argv"], ["program_name"])
        self.assertEqual(result["executable"], "fake_executable_path")
        self.assertTrue(result["frozen"])

    def test_factory_context_composition(self):
        """Test composing contexts using factory patterns."""
        from src.utils.test import runtime_context

        with runtime_context({"sys": {"argv": ["factory_runner"]}}):
            self.assertEqual(sys.argv, ["factory_runner"])

    def test_dynamic_config_generation(self):
        """Test dynamic config generation using factory approach."""

        def create_test_config(test_name):
            return {
                "sys": {"argv": [test_name]},
                "os": {"environ": {f"{test_name.upper()}_VAR": "test_value"}},
            }

        config = create_test_config("dynamic")

        with runtime_context(config):
            self.assertEqual(sys.argv, ["dynamic"])
            self.assertEqual(os.environ["DYNAMIC_VAR"], "test_value")


if __name__ == "__main__":
    unittest.main()
