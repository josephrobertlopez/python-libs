"""
Consolidated Test Framework

This package provides a streamlined, runtime-configurable test annotation framework
that consolidates multiple testing utilities into a cohesive, easy-to-use system.

The framework is built around three core modules:
- runtime_annotations: Runtime-configurable test decorators and presets
- mock_utilities: Smart mocking context managers and utilities  
- test_base: Base test classes and common patterns

Key Features:
- Runtime configuration of test mocks and annotations
- Preset and template-based test configurations
- Smart context management with automatic cleanup
- Support for both unittest and pytest patterns
- Backward compatibility with existing test code
- Dramatic reduction in test boilerplate

Quick Start:
    from src.utils.test import runtime_mock, StandardTestCase
    
    class MyTests(StandardTestCase):
        @runtime_mock("minimal")
        def test_with_preset(self):
            # Test code here
            pass
"""

# =============================================================================
# CORE FRAMEWORK IMPORTS
# =============================================================================

# Runtime Annotations - Main framework
from .runtime_annotations import (
    RuntimeConfig,
    RuntimeContext,
    runtime_mock,
    runtime_context,
    create_preset,
    list_presets,
    create_template,
    list_templates,
    framework_info,
    list_available_presets,
    RuntimeTestCase,
    ASTAnalyzer,
    auto_analyze,
    intelligent_preset,
    smart_mock_auto,
)

# Mock Utilities - Context managers and utilities
from .mock_utilities import (
    # Core smart mock
    smart_mock,
    smart_patches,
    # Quick utilities
    temporary_mock,
    patch_object,
    # Advanced utilities
    MockFactory,
    MockBuilder,
    SmartMockContext,
    SmartPatcher,
    # Introspection
    MockInspector,
    # Legacy compatibility
    create_mock_class,
)

# Test Base - Base classes and patterns
from .test_base import (
    BaseTestCase,
    SmartMockTestCase,
    RuntimeTestCase,
    ParametrizedTestCase,
    PytestBase,
    StandardTestCase,
    StandardPytestBase,
    AssertionHelpers,
    CommonFixtures,
    TestUtilities,
    RuntimeMockMixin,
    AssertionMixin,
    FixtureMixin,
    SmartTestCase,
)

# =============================================================================
# BACKWARD COMPATIBILITY - Legacy imports
# =============================================================================

# Import legacy decorators and classes for backward compatibility
try:
    from .shared_annotations import (
        mock_test_sys,
        mock_test_os,
        mock_test_builtins,
        mock_test_module,
        output_test,
        file_system_test,
        runner_test,
        audio_test,
        mock_runner_context,
        mock_audio_context,
        mock_logging_context,
    )

    _LEGACY_SHARED_AVAILABLE = True
except ImportError:
    _LEGACY_SHARED_AVAILABLE = False

try:
    from .smart_annotations import (
        mock_sys,
        mock_os,
        mock_builtins,
        mock_module,
        mock_output,
        mock_env_vars,
        mock_file_system,
    )

    _LEGACY_SMART_AVAILABLE = True
except ImportError:
    _LEGACY_SMART_AVAILABLE = False

try:
    from .config_mock_factory import ConfigMockFactory

    _LEGACY_CONFIG_AVAILABLE = True
except ImportError:
    _LEGACY_CONFIG_AVAILABLE = False

try:
    from .default_mocks import get_default_preset

    _LEGACY_DEFAULTS_AVAILABLE = True
except ImportError:
    _LEGACY_DEFAULTS_AVAILABLE = False

# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def quick_mock(preset_name: str, **overrides):
    """Quick decorator factory for common mock presets."""
    return runtime_mock(preset_name, **overrides)


def create_test_builder():
    """Create a mock builder for complex test configurations."""
    return MockBuilder()


def create_runtime_config():
    """Create a new runtime configuration instance."""
    return RuntimeConfig()


def inspect_test_context(context):
    """Inspect a test context and return debugging information."""
    return MockInspector.inspect_context(context)


# =============================================================================
# FRAMEWORK INFORMATION
# =============================================================================


def get_framework_info():
    """Get information about the consolidated framework."""
    return {
        "version": "2.0.0",
        "name": "Consolidated Test Framework",
        "core_modules": ["runtime_annotations", "mock_utilities", "test_base"],
        "legacy_compatibility": {
            "shared_annotations": _LEGACY_SHARED_AVAILABLE,
            "smart_annotations": _LEGACY_SMART_AVAILABLE,
            "config_mock_factory": _LEGACY_CONFIG_AVAILABLE,
            "default_mocks": _LEGACY_DEFAULTS_AVAILABLE,
        },
        "features": [
            "Runtime-configurable test annotations",
            "Smart context management",
            "Preset and template configurations",
            "Automatic cleanup and restoration",
            "Multi-framework support (unittest/pytest)",
            "Advanced mock introspection",
            "Backward compatibility",
            "AST-enhanced intelligent testing",
        ],
    }


def print_framework_help():
    """Print comprehensive help for the framework."""
    help_text = """
    Smart Annotation Test Framework - Quick Reference
    
    == BASIC USAGE ==
    
    1. Runtime Mock Decorator:
       @runtime_mock("minimal")
       def test_method(self): ...
    
    2. Context Manager:
       with runtime_context({"sys": {"argv": ["test"]}}) as ctx:
           # Test code
    
    3. Smart Mock Context:
       with smart_mock("sys", argv=["test"]) as ctx:
           # Test code
    
    == BASE CLASSES ==
    
    - StandardTestCase: Complete unittest.TestCase with all features
    - StandardPytestBase: Complete pytest base with all features
    - RuntimeTestCase: Base class with runtime annotation support
    - SmartMockTestCase: Base class with smart mock integration
    - SmartTestCase: AST-enhanced test base class
    
    == PRESETS ==
    
    Available presets: minimal, standard, cli_app, file_operations, 
                      network, audio, database
    
    Usage: @runtime_mock("cli_app", argv=["myprogram", "--verbose"])
    
    == SHARED ANNOTATIONS ==
    
    High-level convenience decorators:
    @runner_test(argv=["test"])       # CLI app testing
    @audio_test()                     # Audio/pygame testing  
    @output_test()                    # Capture stdout/stderr
    @file_system_test(files_exist={}) # File system mocking
    
    == MORE INFO ==
    
    Call get_framework_info() for detailed framework information
    """
    print(help_text)


# =============================================================================
# MAIN EXPORTS
# =============================================================================

__all__ = [
    # Core runtime annotations
    "runtime_mock",
    "runtime_context",
    "RuntimeConfig",
    "RuntimeContext",
    "ASTAnalyzer",
    "auto_analyze",
    "intelligent_preset",
    "smart_mock_auto",
    # Mock utilities
    "smart_mock",
    "smart_patches",
    "temporary_mock",
    "patch_object",
    "MockFactory",
    "MockBuilder",
    "SmartMockContext",
    "SmartPatcher",
    "MockInspector",
    # Base classes
    "StandardTestCase",
    "StandardPytestBase",
    "RuntimeTestCase",
    "SmartMockTestCase",
    "BaseTestCase",
    "PytestBase",
    "ParametrizedTestCase",
    # Utilities and helpers
    "AssertionHelpers",
    "CommonFixtures",
    "TestUtilities",
    # Mixins
    "RuntimeMockMixin",
    "AssertionMixin",
    "FixtureMixin",
    # Convenience functions
    "quick_mock",
    "create_test_builder",
    "create_runtime_config",
    "inspect_test_context",
    # Preset and template management
    "create_preset",
    "list_presets",
    "create_template",
    "list_templates",
    # Framework info
    "get_framework_info",
    "print_framework_help",
    "framework_info",
    "list_available_presets",
    "SmartTestCase",
]

# Add legacy exports if available
if _LEGACY_SHARED_AVAILABLE:
    __all__.extend(
        [
            "mock_test_sys",
            "mock_test_os",
            "mock_test_builtins",
            "mock_test_module",
            "output_test",
            "file_system_test",
            "runner_test",
            "audio_test",
        ]
    )

if _LEGACY_SMART_AVAILABLE:
    __all__.extend(
        [
            "mock_sys",
            "mock_os",
            "mock_builtins",
            "mock_module",
            "mock_output",
            "mock_env_vars",
            "mock_file_system",
        ]
    )

if _LEGACY_CONFIG_AVAILABLE:
    __all__.append("ConfigMockFactory")

if _LEGACY_DEFAULTS_AVAILABLE:
    __all__.append("get_default_preset")

# =============================================================================
# VERSION AND METADATA
# =============================================================================

__version__ = "2.0.0"
__author__ = "Test Framework Team"
__description__ = "Consolidated runtime-configurable test annotation framework"
