"""
Runtime Test Annotations Framework

Consolidated testing framework that provides runtime-configurable test annotations
with dramatically reduced boilerplate. This is the primary interface for all test mocking.

Features:
- Runtime annotation configuration
- Template-based mock setups
- Decorator composition
- Context manager support
- Preset configurations
- Dynamic mock updates
- AST analysis capabilities and intelligent pattern detection

Usage:
    # Simple runtime decorator
    @runtime_mock("standard")  # Uses preset configuration
    def test_basic():
        pass

    # Custom runtime configuration  
    @runtime_mock({
        "sys": {"argv": ["myapp", "--debug"]},
        "os": {"environ": {"DEBUG": "1"}}
    })
    def test_custom():
        pass
        
    # Template-based with variables
    @runtime_mock("cli_app", program="myapp", args=["--verbose"])
    def test_template():
        pass
        
    # Context manager for dynamic updates
    def test_dynamic():
        with runtime_context("standard") as ctx:
            # Standard mocks active
            ctx.update("sys", "argv", ["new", "args"])
            # Updated mocks now active
"""

import functools
import json
import textwrap
from typing import Any, Dict, List, Set, Optional, Union, Callable
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from contextlib import contextmanager
from io import StringIO
import inspect
import ast
import re
import importlib
import sys
import os


# =============================================================================
# RUNTIME CONFIGURATION SYSTEM
# =============================================================================


class RuntimeConfig:
    """Runtime configuration for test annotations."""

    def __init__(self, config: Union[str, Dict[str, Any]], **variables):
        """Initialize with preset name, config dict, or template variables."""
        if isinstance(config, str):
            if config in PRESET_CONFIGS:
                self.config = PRESET_CONFIGS[config].copy()
            elif config in TEMPLATE_CONFIGS:
                self.config = self._render_template(TEMPLATE_CONFIGS[config], variables)
            else:
                raise ValueError(f"Unknown preset or template: {config}")
        else:
            self.config = config.copy()

        # Apply any additional variables by merging them with the base config
        if variables:
            self._merge_config_variables(variables)

    def _render_template(
        self, template: Dict[str, Any], variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Render template with variables."""
        return self._substitute_variables(template, variables)

    def _substitute_variables(self, obj: Any, variables: Dict[str, Any]) -> Any:
        """Recursively substitute template variables."""
        if isinstance(obj, dict):
            return {k: self._substitute_variables(v, variables) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_variables(item, variables) for item in obj]
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            var_name = obj[2:-1]
            return variables.get(var_name, obj)
        else:
            return obj

    def _merge_config_variables(self, variables: Dict[str, Any]):
        """Merge additional variables into the base config."""
        for module_path, module_config in variables.items():
            if module_path in self.config:
                self.config[module_path].update(module_config)
            else:
                self.config[module_path] = module_config


# =============================================================================
# RUNTIME CONTEXT MANAGER
# =============================================================================


class RuntimeContext:
    """Runtime context manager for dynamic mock management."""

    def __init__(self, config: Union[RuntimeConfig, Dict[str, Any]]):
        if isinstance(config, RuntimeConfig):
            self.config = config.config
        else:
            # Handle raw dictionary config
            self.config = config
        self.active_patches = {}
        self.mock_values = {}

    def __enter__(self):
        """Start all configured mocks."""
        for module_path, module_config in self.config.items():
            self._apply_module_mocks(module_path, module_config)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up all active patches."""
        for patches in self.active_patches.values():
            for patcher in patches:
                try:
                    patcher.stop()
                except Exception:
                    pass  # Ignore cleanup errors
        self.active_patches.clear()
        self.mock_values.clear()

    def _apply_module_mocks(self, module_path: str, config: Dict[str, Any]):
        """Apply mocks for a specific module."""
        patches = []

        for attr_name, mock_value in config.items():
            full_path = f"{module_path}.{attr_name}"

            try:
                # Special handling for os.environ - update instead of replace
                if full_path == "os.environ" and isinstance(mock_value, dict):
                    import os

                    # Save original values to restore later
                    original_values = {}
                    for key, value in mock_value.items():
                        if key in os.environ:
                            original_values[key] = os.environ[key]
                        os.environ[key] = str(value)

                    # Create a cleanup function to restore original values
                    def cleanup_environ():
                        for key in mock_value.keys():
                            if key in original_values:
                                os.environ[key] = original_values[key]
                            elif key in os.environ:
                                del os.environ[key]

                    # Store cleanup function for later
                    patches.append(type("EnvCleanup", (), {"stop": cleanup_environ})())
                    continue

                # Handle nested attributes like os.path.join
                if isinstance(mock_value, dict):
                    # For nested configs, apply each sub-attribute individually
                    for sub_attr, sub_value in mock_value.items():
                        nested_path = f"{full_path}.{sub_attr}"
                        try:
                            if callable(sub_value) and not isinstance(sub_value, type):
                                patcher = patch(nested_path, side_effect=sub_value)
                            else:
                                patcher = patch(nested_path, sub_value)
                            patcher.start()
                            patches.append(patcher)
                            self.mock_values[nested_path] = sub_value
                        except Exception:
                            # Skip individual nested patches that fail
                            continue
                else:
                    # Handle direct attributes
                    # Check if attribute might not exist (like sys.frozen)
                    needs_create = False
                    if module_path == "sys" and attr_name == "frozen":
                        needs_create = True

                    if callable(mock_value) and not isinstance(mock_value, type):
                        # Use side_effect for callables
                        patcher = patch(
                            full_path, side_effect=mock_value, create=needs_create
                        )
                    else:
                        # Direct replacement for values and types
                        patcher = patch(full_path, mock_value, create=needs_create)

                    patcher.start()
                    patches.append(patcher)
                    self.mock_values[full_path] = mock_value

            except Exception as e:
                # If patch fails, try as attribute patch
                try:
                    import importlib

                    module = importlib.import_module(module_path)
                    if isinstance(mock_value, dict):
                        # Create a mock object with the nested attributes
                        from unittest.mock import MagicMock

                        mock_obj = MagicMock()
                        for sub_attr, sub_value in mock_value.items():
                            setattr(mock_obj, sub_attr, sub_value)
                        patcher = patch.object(module, attr_name, mock_obj)
                    else:
                        patcher = patch.object(module, attr_name, mock_value)
                    patcher.start()
                    patches.append(patcher)
                    self.mock_values[full_path] = mock_value
                except Exception:
                    # Skip failed patches but continue with others
                    print(f"Warning: Could not patch {full_path}: {e}")

        self.active_patches[module_path] = patches

    def update(self, module_path: str, attr_name: str, new_value: Any):
        """Update a mock value at runtime."""
        full_path = f"{module_path}.{attr_name}"

        # Stop existing patch if it exists
        if module_path in self.active_patches:
            for patcher in self.active_patches[module_path]:
                if hasattr(patcher, "attribute") and patcher.attribute == attr_name:
                    patcher.stop()
                    self.active_patches[module_path].remove(patcher)
                    break

        # Apply new patch
        try:
            if callable(new_value) and not isinstance(new_value, type):
                patcher = patch(full_path, side_effect=new_value)
            else:
                patcher = patch(full_path, new_value)

            patcher.start()

            if module_path not in self.active_patches:
                self.active_patches[module_path] = []
            self.active_patches[module_path].append(patcher)
            self.mock_values[full_path] = new_value

        except Exception as e:
            print(f"Warning: Could not update {full_path}: {e}")

    def get_mock(self, module_path: str, attr_name: str) -> Any:
        """Get current mock value."""
        full_path = f"{module_path}.{attr_name}"
        return self.mock_values.get(full_path)


# =============================================================================
# AST ANALYSIS ENGINE
# =============================================================================


class ASTAnalyzer:
    """AST-based code analysis for intelligent test configuration."""

    def __init__(self):
        self.detected_patterns = set()
        self.detected_imports = set()
        self.detected_calls = set()
        self.recommended_presets = []

    def analyze_function(self, func: Callable) -> Dict[str, Any]:
        """Analyze a test function using AST to detect patterns and requirements."""
        try:
            source = inspect.getsource(func)
            source = textwrap.dedent(source)  # Normalize indentation
            tree = ast.parse(source)

            analysis = {
                "imports": self._extract_imports(tree),
                "function_calls": self._extract_function_calls(tree),
                "patterns": self._detect_patterns(tree, source),
                "recommended_preset": self._recommend_preset(tree, source),
                "complexity_score": self._calculate_complexity(tree),
                "auto_mocks": self._generate_auto_mocks(tree, source),
            }

            return analysis

        except (OSError, TypeError):
            # Fallback for functions without source (built-ins, etc.)
            return {
                "imports": set(),
                "function_calls": set(),
                "patterns": set(),
                "recommended_preset": "minimal",
                "complexity_score": 1,
                "auto_mocks": {},
            }

    def _extract_imports(self, tree: ast.AST) -> Set[str]:
        """Extract all import statements from AST."""
        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.add(f"{module}.{alias.name}" if module else alias.name)

        return imports

    def _extract_function_calls(self, tree: ast.AST) -> Set[str]:
        """Extract function calls from AST."""
        calls = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    # Handle method calls like obj.method()
                    attr_chain = []
                    current = node.func
                    while isinstance(current, ast.Attribute):
                        attr_chain.append(current.attr)
                        current = current.value
                    if isinstance(current, ast.Name):
                        attr_chain.append(current.id)
                    calls.add(".".join(reversed(attr_chain)))

        return calls

    def _detect_patterns(self, tree: ast.AST, source: str) -> Set[str]:
        """Detect common test patterns from AST and source."""
        patterns = set()

        # Pattern detection rules
        pattern_rules = {
            "logging_system": ["logging", "getLogger", "LoggingConfig"],
            "file_operations": ["open", "pathlib", "os.path", "Path"],
            "cli_application": ["sys.argv", "argparse", "ArgumentParser"],
            "audio_system": ["pygame", "mixer", "sound"],
            "network_requests": ["requests", "urllib", "http"],
            "database_operations": ["sqlite3", "mysql", "postgres"],
            "environment_vars": ["os.environ", "getenv", "setenv"],
            "singleton_pattern": ["Singleton", "__new__", "instance"],
            "datetime_operations": ["datetime", "time", "strftime"],
            "json_operations": ["json", "loads", "dumps"],
            "subprocess_calls": ["subprocess", "Popen", "run"],
        }

        for pattern_name, indicators in pattern_rules.items():
            if any(indicator in source for indicator in indicators):
                patterns.add(pattern_name)

        return patterns

    def _recommend_preset(self, tree: ast.AST, source: str) -> str:
        """Recommend the best preset based on detected patterns."""
        patterns = self._detect_patterns(tree, source)

        # Preset recommendation logic
        if "logging_system" in patterns and "file_operations" in patterns:
            return "logging_system"
        elif "cli_application" in patterns:
            return "cli_app"
        elif "audio_system" in patterns:
            return "audio_app"
        elif "network_requests" in patterns:
            return "network_app"
        elif "file_operations" in patterns:
            return "file_system"
        elif "environment_vars" in patterns:
            return "environment"
        else:
            return "minimal"

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate test complexity score."""
        complexity = 1

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += 1
            elif isinstance(node, ast.With):
                complexity += 1

        return complexity

    def _generate_auto_mocks(self, tree: ast.AST, source: str) -> Dict[str, Any]:
        """Generate automatic mock configurations based on detected usage."""
        auto_mocks = {}
        imports = self._extract_imports(tree)

        # Auto-mock generation rules
        if "sys" in imports or "sys.argv" in source:
            auto_mocks["sys"] = {
                "argv": ["test", "--auto-detected"],
                "stdout": StringIO(),
                "stderr": StringIO(),
            }

        if "os" in imports or "os.environ" in source:
            auto_mocks["os"] = {
                "environ": {"AUTO_DETECTED": "true", "TEST_MODE": "ast"},
                "path.exists": lambda x: True,
                "makedirs": Mock(),
            }

        if "logging" in imports:
            auto_mocks["logging"] = {
                "getLogger": lambda name=None: Mock(),
                "config.fileConfig": Mock(),
            }

        if "pathlib" in imports:
            auto_mocks["pathlib"] = {"Path": Mock}

        return auto_mocks


# Global AST analyzer instance
_ast_analyzer = ASTAnalyzer()


# =============================================================================
# INTELLIGENT DECORATORS
# =============================================================================


def auto_analyze(
    func: Callable = None,
    *,
    detect_patterns: Optional[List[str]] = None,
    override_preset: Optional[str] = None,
    enable_auto_mocks: bool = True,
) -> Callable:
    """
    AST-based automatic test analysis and configuration.

    This decorator analyzes the test function's source code using AST to:
    - Detect import patterns and usage
    - Identify common test scenarios
    - Automatically apply optimal mock configurations
    - Recommend and apply the best preset

    Args:
        detect_patterns: Specific patterns to detect (optional)
        override_preset: Override the automatically detected preset
        enable_auto_mocks: Whether to apply automatic mocks
    """

    def decorator(test_func: Callable) -> Callable:
        @functools.wraps(test_func)
        def wrapper(*args, **kwargs):
            # Perform AST analysis
            analysis = _ast_analyzer.analyze_function(test_func)

            # Determine preset to use
            preset_name = override_preset or analysis["recommended_preset"]

            # Filter patterns if specified
            if detect_patterns:
                analysis["patterns"] = {
                    p for p in analysis["patterns"] if p in detect_patterns
                }

            # Apply preset configuration first
            if preset_name in PRESET_CONFIGS:
                preset_config = RuntimeConfig(preset_name)
                with RuntimeContext(preset_config) as preset_ctx:
                    # Apply additional auto-mocks if enabled and they don't conflict
                    if enable_auto_mocks and analysis["auto_mocks"]:
                        # Only add auto_mocks that don't conflict with preset
                        additional_mocks = {}
                        for module, mocks in analysis["auto_mocks"].items():
                            if module not in preset_config.config:
                                additional_mocks[module] = mocks

                        if additional_mocks:
                            with RuntimeContext(additional_mocks) as auto_ctx:
                                return test_func(*args, **kwargs)
                        else:
                            return test_func(*args, **kwargs)
                    else:
                        return test_func(*args, **kwargs)
            else:
                # No preset, just use auto_mocks
                if enable_auto_mocks and analysis["auto_mocks"]:
                    with RuntimeContext(analysis["auto_mocks"]) as ctx:
                        return test_func(*args, **kwargs)
                else:
                    return test_func(*args, **kwargs)

        # Attach analysis metadata to function
        wrapper._ast_analysis = _ast_analyzer.analyze_function(test_func)
        wrapper._auto_analyze = True

        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)


def intelligent_preset(preset_name: str, **overrides) -> Callable:
    """
    Intelligent preset decorator with AST validation.

    Applies a preset but validates it against AST analysis to ensure
    compatibility and provide warnings for suboptimal configurations.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Analyze function to validate preset choice
            analysis = _ast_analyzer.analyze_function(func)
            recommended = analysis["recommended_preset"]

            # Warn if preset doesn't match analysis
            if preset_name != recommended and preset_name != "custom":
                print(
                    f"⚠️  AST Analysis: Function {func.__name__} would benefit from '{recommended}' preset instead of '{preset_name}'"
                )

            # Apply the requested preset with overrides
            config = RuntimeConfig(preset_name, **overrides)
            with RuntimeContext(config) as ctx:
                return func(*args, **kwargs)

        wrapper._intelligent_preset = preset_name
        wrapper._ast_analysis = _ast_analyzer.analyze_function(func)

        return wrapper

    return decorator


def smart_mock_auto(module_path: str, **overrides) -> Callable:
    """
    Smart mock decorator with automatic configuration based on AST analysis.

    Analyzes how the module is used in the test and applies intelligent defaults.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            analysis = _ast_analyzer.analyze_function(func)

            # Get auto-generated mocks for this module
            auto_mocks = analysis["auto_mocks"].get(module_path, {})

            # Merge with manual overrides (manual takes precedence)
            final_config = {**auto_mocks, **overrides}

            # Apply smart mock with intelligent configuration
            from .mock_utilities import smart_mock

            with smart_mock(module_path, **final_config) as ctx:
                return func(*args, **kwargs)

        wrapper._smart_mock_auto = module_path
        return wrapper

    return decorator


# =============================================================================
# RUNTIME DECORATORS
# =============================================================================


def runtime_mock(config: Union[str, Dict[str, Any]], **variables):
    """Primary runtime mock decorator."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            runtime_config = RuntimeConfig(config, **variables)
            with RuntimeContext(runtime_config):
                return func(*args, **kwargs)

        return wrapper

    return decorator


@contextmanager
def runtime_context(config: Union[str, Dict[str, Any]], **variables):
    """Runtime context manager."""
    runtime_config = RuntimeConfig(config, **variables)
    with RuntimeContext(runtime_config) as ctx:
        yield ctx


# =============================================================================
# PRESET CONFIGURATIONS
# =============================================================================

PRESET_CONFIGS = {
    "minimal": {"sys": {"argv": ["test"], "stdout": StringIO(), "stderr": StringIO()}},
    "standard": {
        "sys": {
            "argv": ["program"],
            "executable": "/usr/bin/python3",
            "stdout": StringIO(),
            "stderr": StringIO(),
            "platform": "linux",
        },
        "os": {
            "environ": {
                "HOME": "/home/testuser",
                "PATH": "/usr/bin:/bin",
                "TEST_ENV": "true",
            },
            "getcwd": lambda: "/test/dir",
            "listdir": lambda path=".": ["file1.txt", "file2.py"],
            "path": {
                "exists": lambda path: True,
                "join": lambda *args: "/".join(str(arg) for arg in args),
            },
        },
        "builtins": {
            "open": lambda filename, mode="r", **kwargs: StringIO("test content"),
            "print": Mock(),
            "input": lambda prompt="": "test_input",
        },
    },
    "cli_app": {
        "sys": {
            "argv": ["app", "--help"],
            "executable": "/usr/bin/python3",
            "stdout": StringIO(),
            "stderr": StringIO(),
        },
        "os": {
            "environ": {"HOME": "/home/user", "PATH": "/usr/bin"},
            "getcwd": lambda: "/app/dir",
            "path": {
                "exists": lambda path: True,
                "join": lambda *args: "/".join(str(arg) for arg in args),
            },
        },
    },
    "file_operations": {
        "os": {
            "path": {
                "exists": lambda path: path in ["/test/file.txt", "/config.json"],
                "isfile": lambda path: not path.endswith("/"),
                "isdir": lambda path: path.endswith("/"),
                "join": lambda *args: "/".join(str(arg) for arg in args),
            }
        },
        "builtins": {"open": lambda f, mode="r": StringIO("mock file content")},
    },
    "network": {
        "requests": {
            "get": lambda url, **kwargs: Mock(
                status_code=200,
                json=lambda: {"success": True, "url": url},
                text="mock response",
            ),
            "post": lambda url, **kwargs: Mock(status_code=201),
        },
        "urllib": {
            "request": {
                "urlopen": lambda url: Mock(
                    read=lambda: b"mock response", getcode=lambda: 200
                )
            }
        },
    },
    "audio": {
        "pygame": {
            "mixer": {
                "init": Mock(),
                "quit": Mock(),
                "Sound": Mock,
                "music": {"play": Mock(), "stop": Mock(), "get_busy": lambda: False},
            }
        },
        "os": {"environ": {"SDL_AUDIODRIVER": "dummy"}},
    },
    "audio_system": {
        "pygame": {
            "mixer": {
                "init": Mock(),
                "quit": Mock(),
                "Sound": Mock,
                "music": {"play": Mock(), "stop": Mock(), "get_busy": lambda: False},
            }
        },
        "os": {"environ": {"SDL_AUDIODRIVER": "dummy"}},
    },
    "database": {
        "sqlite3": {
            "connect": lambda db: Mock(
                execute=Mock(),
                commit=Mock(),
                close=Mock(),
                cursor=lambda: Mock(
                    execute=Mock(),
                    fetchall=lambda: [("test", "data")],
                    fetchone=lambda: ("test", "data"),
                ),
            )
        }
    },
    "logging_system": {
        "logging": {
            "getLogger": lambda name=None: Mock(
                info=Mock(),
                debug=Mock(),
                warning=Mock(),
                error=Mock(),
                critical=Mock(),
                setLevel=Mock(),
                addHandler=Mock(),
            ),
            "basicConfig": Mock(),
            "config": {"fileConfig": Mock()},
        },
        "os": {
            "path": {
                "exists": lambda path: True,
                "join": lambda *args: "/".join(str(arg) for arg in args),
            }
        },
    },
    "file_system": {
        "os": {
            "path": {
                "exists": lambda path: path in ["/test/file.txt", "/config/app.conf"],
                "isfile": lambda path: not path.endswith("/"),
                "isdir": lambda path: path.endswith("/"),
                "join": lambda *args: "/".join(str(arg) for arg in args),
            },
            "makedirs": Mock(),
            "environ": {"HOME": "/home/test", "TEST_MODE": "ast"},
        },
        "pathlib": {"Path": Mock},
        "builtins": {"open": lambda f, mode="r": StringIO("test file content")},
    },
}


# =============================================================================
# TEMPLATE CONFIGURATIONS
# =============================================================================

TEMPLATE_CONFIGS = {
    "cli_app": {
        "sys": {
            "argv": ["${program}", "${args}"],
            "executable": "/usr/bin/python3",
            "stdout": StringIO(),
            "stderr": StringIO(),
        },
        "os": {
            "environ": {"${env_vars}": "${env_values}"},
            "getcwd": lambda: "${working_dir}",
            "path": {
                "exists": lambda path: True,
                "join": lambda *args: "/".join(str(arg) for arg in args),
            },
        },
    },
    "web_service": {
        "requests": {
            "get": lambda url, **kwargs: Mock(
                status_code="${status_code}",
                json=lambda: {"${response_key}": "${response_value}"},
            )
        }
    },
    "file_processor": {
        "os": {
            "path": {
                "exists": lambda path: path in "${existing_files}",
                "isfile": lambda path: not path.endswith("/"),
            }
        },
        "builtins": {"open": lambda f, mode="r": StringIO("${file_content}")},
    },
}


# =============================================================================
# CONVENIENCE ALIASES AND SHORTCUTS
# =============================================================================

# Convenience decorators for common scenarios
mock_sys = lambda **kwargs: runtime_mock({"sys": kwargs})
mock_os = lambda **kwargs: runtime_mock({"os": kwargs})
mock_builtins = lambda **kwargs: runtime_mock({"builtins": kwargs})
mock_module = lambda module_path, **kwargs: runtime_mock({module_path: kwargs})

# Context manager aliases
smart_mock = runtime_context
smart_patches = runtime_context


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def create_preset(name: str, config: Dict[str, Any]):
    """Create a new preset configuration."""
    PRESET_CONFIGS[name] = config


def create_template(name: str, config: Dict[str, Any]):
    """Create a new template configuration."""
    TEMPLATE_CONFIGS[name] = config


def list_presets() -> List[str]:
    """List all available presets."""
    return list(PRESET_CONFIGS.keys())


def list_templates() -> List[str]:
    """List all available templates."""
    return list(TEMPLATE_CONFIGS.keys())


def load_config_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Load configuration from JSON/YAML file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {file_path}")

    with open(path, "r") as f:
        if path.suffix.lower() == ".json":
            return json.load(f)
        elif path.suffix.lower() in [".yaml", ".yml"]:
            try:
                import yaml

                return yaml.safe_load(f)
            except ImportError:
                raise ImportError("PyYAML required for YAML config files")
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")


def framework_info() -> Dict[str, Any]:
    """Get comprehensive framework information."""
    return {
        "version": "1.0.0",
        "available_presets": list_presets(),
        "available_templates": list_templates(),
        "features": [
            "Runtime mock configuration",
            "AST-based intelligent analysis",
            "AST-enhanced intelligent testing",
            "Template-based mock setups",
            "Automatic pattern detection",
            "Context manager support",
        ],
        "preset_count": len(PRESET_CONFIGS),
        "template_count": len(TEMPLATE_CONFIGS),
    }


# Alias for backward compatibility
list_available_presets = list_presets


# =============================================================================
# TEST BASE CLASSES FOR INHERITANCE
# =============================================================================


class RuntimeTestCase:
    """Base test case with runtime mock utilities."""

    def setup_mocks(self, config: Union[str, Dict[str, Any]], **variables):
        """Set up mocks for the test case."""
        self._runtime_config = RuntimeConfig(config, **variables)
        self._runtime_context = RuntimeContext(self._runtime_config)
        self._runtime_context.__enter__()

    def teardown_mocks(self):
        """Clean up mocks."""
        if hasattr(self, "_runtime_context"):
            self._runtime_context.__exit__(None, None, None)

    def update_mock(self, module_path: str, attr_name: str, new_value: Any):
        """Update a mock at runtime."""
        if hasattr(self, "_runtime_context"):
            self._runtime_context.update(module_path, attr_name, new_value)


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

"""
EXAMPLES:

1. Simple preset usage:
    @runtime_mock("standard")
    def test_basic_functionality():
        import sys, os
        assert sys.argv == ["program"]
        assert os.getcwd() == "/test/dir"

2. Custom configuration:
    @runtime_mock({
        "sys": {"argv": ["myapp", "--debug"]},
        "os": {"environ": {"DEBUG": "1"}}
    })
    def test_debug_mode():
        import sys, os
        assert "--debug" in sys.argv
        assert os.environ["DEBUG"] == "1"

3. Template with variables:
    @runtime_mock("cli_app", 
                  program="myapp",
                  args=["--verbose", "--output", "result.txt"],
                  working_dir="/project")
    def test_cli_with_args():
        import sys
        assert sys.argv == ["myapp", "--verbose", "--output", "result.txt"]

4. Dynamic context management:
    def test_dynamic_updates():
        with runtime_context("standard") as ctx:
            import sys
            assert sys.argv == ["program"]
            
            # Update at runtime
            ctx.update("sys", "argv", ["newprogram", "--flag"])
            assert sys.argv == ["newprogram", "--flag"]

5. Test class inheritance:
    class TestMyApp(RuntimeTestCase):
        def setUp(self):
            self.setup_mocks("cli_app", program="myapp")
            
        def tearDown(self):
            self.teardown_mocks()
            
        def test_app_behavior(self):
            import sys
            assert sys.argv[0] == "myapp"

6. Creating custom presets:
    create_preset("my_app", {
        "sys": {"argv": ["myapp"]},
        "mymodule": {"config": {"debug": True}}
    })
    
    @runtime_mock("my_app")
    def test_my_app():
        pass
"""

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core classes
    "RuntimeConfig",
    "RuntimeContext",
    "ASTAnalyzer",
    # Runtime decorators
    "runtime_mock",
    "runtime_preset",
    "runtime_template",
    # AST-enhanced decorators
    "auto_analyze",
    "intelligent_preset",
    "smart_mock_auto",
    # Configuration data
    "PRESET_CONFIGS",
    "TEMPLATE_CONFIGS",
    # Convenience functions
    "get_preset_info",
    "list_available_presets",
    "create_custom_preset",
    "framework_info",
    "list_presets",
    # Module-level objects (for import by other modules)
    "_ast_analyzer",
    # Legacy aliases
    "mock_sys",
    "mock_os",
    "mock_builtins",
    "mock_module",
    "smart_mock",
    "smart_patches",
    "RuntimeTestCase",
]
